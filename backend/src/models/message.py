"""Message model for storing conversation history."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class MessageRole(str, Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message in a conversation with tool call metadata."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"nullable": False})
    content: str = Field(sa_column_kwargs={"nullable": False})
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None, sa_column=Column(JSON)
    )
    tool_results: Optional[List[Dict[str, Any]]] = Field(
        default=None, sa_column=Column(JSON)
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
                "role": "user",
                "content": "add buy groceries",
                "tool_calls": None,
                "tool_results": None,
                "timestamp": "2025-12-28T10:15:00Z"
            }
        }
