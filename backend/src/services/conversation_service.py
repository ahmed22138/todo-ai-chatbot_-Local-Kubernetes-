"""Conversation service for managing conversation history and persistence."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationService:
    """Service for managing conversations and message history."""

    async def create_conversation(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> Conversation:
        """Create a new conversation for a user.

        Args:
            session: Database session.
            user_id: UUID of the user.

        Returns:
            Conversation: The newly created conversation.
        """
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    async def get_conversation_by_id(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Optional[Conversation]:
        """Get a conversation by ID, ensuring it belongs to the user.

        Args:
            session: Database session.
            conversation_id: UUID of the conversation.
            user_id: UUID of the user (for authorization).

        Returns:
            Optional[Conversation]: The conversation if found and authorized, None otherwise.
        """
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_conversations_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[dict]:
        """Get all conversations for a user with message counts.

        Args:
            session: Database session.
            user_id: UUID of the user.
            limit: Maximum number of conversations to return.
            offset: Number of conversations to skip (for pagination).

        Returns:
            List[dict]: List of conversations with metadata.
        """
        # Fetch conversations ordered by most recent first
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        conversations = result.scalars().all()

        # Build response with message counts
        conversations_with_counts = []
        for conv in conversations:
            # Count messages in this conversation
            msg_count_query = select(Message).where(
                Message.conversation_id == conv.id
            )
            msg_count_result = await session.execute(msg_count_query)
            message_count = len(msg_count_result.scalars().all())

            conversations_with_counts.append({
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": message_count,
            })

        return conversations_with_counts

    async def fetch_conversation_history(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Fetch all messages in a conversation, ordered by timestamp.

        Args:
            session: Database session.
            conversation_id: UUID of the conversation.
            limit: Optional limit on number of messages to fetch (most recent).

        Returns:
            List[Message]: List of messages ordered by timestamp (oldest first).
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
        )

        if limit:
            # For limited history, get most recent N messages but still return in chronological order
            query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.timestamp.desc())
                .limit(limit)
            )
            result = await session.execute(query)
            messages = list(reversed(result.scalars().all()))
        else:
            result = await session.execute(query)
            messages = result.scalars().all()

        return list(messages)

    async def update_conversation_title(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        title: str,
    ) -> None:
        """Update the conversation's title.

        Args:
            session: Database session.
            conversation_id: UUID of the conversation.
            title: New title for the conversation.
        """
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.title = title[:200]  # Limit to max_length
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            await session.commit()

    async def update_conversation_timestamp(
        self,
        session: AsyncSession,
        conversation_id: UUID,
    ) -> None:
        """Update the conversation's updated_at timestamp.

        Args:
            session: Database session.
            conversation_id: UUID of the conversation.
        """
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            await session.commit()

    async def delete_conversation(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a conversation and all its messages.

        Args:
            session: Database session.
            conversation_id: UUID of the conversation.
            user_id: UUID of the user (for authorization).

        Returns:
            bool: True if deleted, False if not found or unauthorized.
        """
        # Verify ownership
        conversation = await self.get_conversation_by_id(
            session, conversation_id, user_id
        )

        if not conversation:
            return False

        # Delete all messages first
        delete_msgs_query = select(Message).where(
            Message.conversation_id == conversation_id
        )
        msgs_result = await session.execute(delete_msgs_query)
        messages = msgs_result.scalars().all()

        for msg in messages:
            await session.delete(msg)

        # Delete conversation
        await session.delete(conversation)
        await session.commit()

        return True


# Global conversation service instance
conversation_service = ConversationService()


def get_conversation_service() -> ConversationService:
    """Get the global conversation service instance.

    Returns:
        ConversationService: The conversation service instance.
    """
    return conversation_service
