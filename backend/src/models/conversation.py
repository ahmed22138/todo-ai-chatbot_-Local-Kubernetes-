"""Conversation model for storing chat threads."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship


class Conversation(SQLModel, table=True):
    """Conversation thread between user and AI assistant."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    thread_id: Optional[str] = Field(default=None, max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Shopping list for groceries",
                "created_at": "2025-12-28T10:00:00Z",
                "updated_at": "2025-12-28T11:30:00Z"
            }
        }
