"""MCP tool for adding a new task."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task, TaskStatus


async def add_task(
    session: AsyncSession,
    user_id: UUID,
    title: str,
    description: Optional[str] = None,
) -> dict:
    """Add a new task for the user.

    Args:
        session: Database session.
        user_id: UUID of the user creating the task.
        title: Task title (max 500 characters).
        description: Optional task description.

    Returns:
        dict: Success response with task details and friendly message.

    Example:
        >>> result = await add_task(session, user_id, "Buy groceries", "Milk, eggs, bread")
        >>> print(result["message"])
        "Great! I've added 'Buy groceries' to your task list."
    """
    try:
        # Validate title length
        if len(title) > 500:
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": "Task title is too long (max 500 characters)",
                    "details": {"max_length": 500, "actual_length": len(title)},
                },
                "message": "Oops! Your task title is a bit too long. Could you make it shorter?",
            }

        # Validate title is not empty after trimming
        title = title.strip()
        if not title:
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": "Task title cannot be empty",
                    "details": {},
                },
                "message": "Please provide a task title. What would you like to add?",
            }

        # Create new task
        task = Task(
            user_id=user_id,
            title=title,
            description=description.strip() if description else None,
            status=TaskStatus.INCOMPLETE,
            created_at=datetime.utcnow(),
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
            },
            "message": f"Great! I've added '{title}' to your task list.",
        }

    except Exception as e:
        # Database or system error
        await session.rollback()
        return {
            "success": False,
            "error": {
                "type": "system_error",
                "message": f"Database error: {str(e)}",
                "details": {"exception_type": type(e).__name__},
            },
            "message": "Oops! I had trouble saving your task. Please try again in a moment. If the problem continues, our team has been notified.",
        }


# MCP tool schema for registration
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Add a new task to the user's todo list",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The task title (max 500 characters)",
                "maxLength": 500,
            },
            "description": {
                "type": "string",
                "description": "Optional task description with additional details",
            },
        },
        "required": ["title"],
    },
}
