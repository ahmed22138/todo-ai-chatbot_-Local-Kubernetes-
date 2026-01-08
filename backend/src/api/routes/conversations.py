"""Conversations API routes for managing conversation history."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user_id
from src.db.connection import get_session
from src.services.conversation_service import get_conversation_service

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def list_conversations(
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip (for pagination)"),
):
    """List all conversations for the current user with pagination.

    Args:
        user_id: Current user's ID (from auth middleware).
        session: Database session.
        limit: Maximum number of conversations to return (1-100, default 50).
        offset: Number of conversations to skip for pagination (default 0).

    Returns:
        dict: List of conversations with metadata and message counts.

    Example Response:
        {
            "conversations": [
                {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "created_at": "2025-12-28T10:00:00Z",
                    "updated_at": "2025-12-28T11:30:00Z",
                    "message_count": 15
                }
            ],
            "count": 1,
            "limit": 50,
            "offset": 0
        }
    """
    conversation_service = get_conversation_service()

    conversations = await conversation_service.get_conversations_by_user(
        session, user_id, limit=limit, offset=offset
    )

    return {
        "conversations": conversations,
        "count": len(conversations),
        "limit": limit,
        "offset": offset,
    }


@router.get("/{conversation_id}/messages", status_code=status.HTTP_200_OK)
async def get_conversation_messages(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Optional limit on number of messages"),
):
    """Get all messages in a conversation.

    Args:
        conversation_id: ID of the conversation.
        user_id: Current user's ID (from auth middleware).
        session: Database session.
        limit: Optional limit on number of messages to return (most recent).

    Returns:
        dict: List of messages in the conversation.

    Raises:
        HTTPException: 404 if conversation not found or doesn't belong to user.

    Example Response:
        {
            "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
            "messages": [
                {
                    "id": "770e8400-e29b-41d4-a716-446655440002",
                    "role": "user",
                    "content": "add buy groceries",
                    "tool_calls": null,
                    "tool_results": null,
                    "timestamp": "2025-12-28T10:15:00Z"
                },
                {
                    "id": "770e8400-e29b-41d4-a716-446655440003",
                    "role": "assistant",
                    "content": "Great! I've added 'buy groceries' to your task list.",
                    "tool_calls": [...],
                    "tool_results": [...],
                    "timestamp": "2025-12-28T10:15:05Z"
                }
            ],
            "count": 2
        }
    """
    conversation_service = get_conversation_service()

    # Verify conversation belongs to user
    conversation = await conversation_service.get_conversation_by_id(
        session, conversation_id, user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Conversation not found",
                "message": "I couldn't find that conversation.",
            },
        )

    # Fetch messages
    messages = await conversation_service.fetch_conversation_history(
        session, conversation_id, limit=limit
    )

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


@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Delete a conversation and all its messages.

    Args:
        conversation_id: ID of the conversation to delete.
        user_id: Current user's ID (from auth middleware).
        session: Database session.

    Returns:
        dict: Success confirmation.

    Raises:
        HTTPException: 404 if conversation not found or doesn't belong to user.
    """
    conversation_service = get_conversation_service()

    deleted = await conversation_service.delete_conversation(
        session, conversation_id, user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Conversation not found",
                "message": "I couldn't find that conversation to delete.",
            },
        )

    return {
        "success": True,
        "message": "Conversation deleted successfully.",
        "conversation_id": str(conversation_id),
    }
