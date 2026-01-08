"""Chat API routes for natural language task management."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.api.middleware.auth import get_current_user_id
from src.db.connection import get_session
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.agent_service import get_agent_service
from src.services.conversation_service import get_conversation_service

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: Optional[UUID] = Field(None, description="Optional conversation ID to continue existing conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "add buy groceries",
                "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    conversation_id: UUID = Field(..., description="ID of the conversation")
    message: str = Field(..., description="Assistant's response message")
    tool_calls: Optional[list] = Field(None, description="Tool calls made during processing")
    tool_results: Optional[list] = Field(None, description="Results from tool executions")
    timestamp: datetime = Field(..., description="Timestamp of the response")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
                "message": "Great! I've added 'buy groceries' to your task list.",
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "type": "function",
                        "function": {
                            "name": "add_task",
                            "arguments": {"title": "buy groceries"},
                        },
                    }
                ],
                "tool_results": [
                    {
                        "tool_call_id": "call_abc123",
                        "tool_name": "add_task",
                        "result": {"success": True, "message": "Task added"},
                    }
                ],
                "timestamp": "2025-12-28T12:00:00Z",
            }
        }


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Process a chat message and return AI assistant's response.

    This endpoint:
    1. Creates or fetches the conversation
    2. Stores the user's message
    3. Invokes the AI agent with conversation history
    4. Stores the assistant's message with tool call metadata
    5. Returns the assistant's response

    Args:
        request: Chat request with message and optional conversation_id.
        user_id: Current user's ID (from auth middleware).
        session: Database session.

    Returns:
        ChatResponse: Assistant's response with tool call metadata.

    Raises:
        HTTPException: 404 if conversation not found or doesn't belong to user.
    """
    agent_service = get_agent_service()
    conversation_service = get_conversation_service()

    # Get or create conversation
    if request.conversation_id:
        # Fetch existing conversation using conversation service
        conversation = await conversation_service.get_conversation_by_id(
            session, request.conversation_id, user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Conversation not found",
                    "message": "I couldn't find that conversation. Let's start a new one!",
                },
            )

        # Update conversation timestamp
        await conversation_service.update_conversation_timestamp(
            session, conversation.id
        )

    else:
        # Create new conversation using conversation service
        conversation = await conversation_service.create_conversation(
            session, user_id
        )

    # Store user message
    user_msg = Message(
        id=uuid4(),
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
        timestamp=datetime.utcnow(),
    )
    session.add(user_msg)
    await session.commit()

    # Invoke AI agent with Assistants API (using threads)
    agent_response = await agent_service.invoke_agent(
        session=session,
        user_id=user_id,
        user_message=request.message,
        thread_id=conversation.thread_id,  # Pass existing thread_id or None for new
    )

    # Update conversation with thread_id if it was newly created
    if agent_response.get("thread_id") and not conversation.thread_id:
        conversation.thread_id = agent_response["thread_id"]
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    # Generate conversation title from first message if new conversation
    if not conversation.title and conversation.thread_id:
        title = await agent_service.generate_conversation_title(request.message)
        await conversation_service.update_conversation_title(
            session, conversation.id, title
        )

    # Check if agent invocation failed
    if not agent_response.get("success", True):
        # Return error message but don't fail the request
        error_msg = agent_response.get(
            "message", "I encountered an error processing your request. Please try again."
        )

        # Store error as assistant message
        assistant_msg = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=error_msg,
            timestamp=datetime.utcnow(),
        )
        session.add(assistant_msg)
        await session.commit()

        return ChatResponse(
            conversation_id=conversation.id,
            message=error_msg,
            tool_calls=None,
            tool_results=None,
            timestamp=assistant_msg.timestamp,
        )

    # Store assistant message with tool call metadata
    assistant_msg = Message(
        id=uuid4(),
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=agent_response["message"],
        tool_calls=agent_response.get("tool_calls"),
        tool_results=agent_response.get("tool_results"),
        timestamp=datetime.utcnow(),
    )
    session.add(assistant_msg)
    await session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message=agent_response["message"],
        tool_calls=agent_response.get("tool_calls"),
        tool_results=agent_response.get("tool_results"),
        timestamp=assistant_msg.timestamp,
    )


@router.get("/conversations", status_code=status.HTTP_200_OK)
async def list_conversations(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """List all conversations for the current user.

    Args:
        user_id: Current user's ID (from auth middleware).
        session: Database session.

    Returns:
        dict: List of conversations with metadata.
    """
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await session.execute(query)
    conversations = result.scalars().all()

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ],
        "count": len(conversations),
    }


@router.get("/conversations/{conversation_id}/messages", status_code=status.HTTP_200_OK)
async def get_conversation_messages(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Get all messages in a conversation.

    Args:
        conversation_id: ID of the conversation.
        user_id: Current user's ID (from auth middleware).
        session: Database session.

    Returns:
        dict: List of messages in the conversation.

    Raises:
        HTTPException: 404 if conversation not found or doesn't belong to user.
    """
    # Verify conversation belongs to user
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    conv_result = await session.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Conversation not found",
                "message": "I couldn't find that conversation.",
            },
        )

    # Fetch messages
    msg_query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
    )
    msg_result = await session.execute(msg_query)
    messages = msg_result.scalars().all()

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "tool_results": msg.tool_results,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ],
        "count": len(messages),
    }
