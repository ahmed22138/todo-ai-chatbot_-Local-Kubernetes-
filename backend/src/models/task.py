"""Task model for todo items."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    """Task completion status."""

    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class Task(SQLModel, table=True):
    """Todo task item."""

    __tablename__ = "tasks"

    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500, sa_column_kwargs={"nullable": False})
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.INCOMPLETE, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "incomplete",
                "created_at": "2025-12-28T10:20:00Z",
                "completed_at": None
            }
        }
