"""MCP tool for updating a task."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def update_task(
    session: AsyncSession,
    user_id: UUID,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Update a task's title and/or description.

    Args:
        session: Database session.
        user_id: UUID of the user.
        task_id: ID of the task to update.
        title: Optional new title.
        description: Optional new description.

    Returns:
        dict: Success response with confirmation.

    Example:
        >>> result = await update_task(session, user_id, 123, title="Buy organic groceries")
        >>> print(result["message"])
        "Got it! I've updated 'Buy organic groceries'."
    """
    try:
        # Validate at least one field is provided
        if title is None and description is None:
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": "No updates provided",
                    "details": {},
                },
                "message": "What would you like me to update? Please provide a new title or description.",
            }

        # Validate and sanitize title if provided
        if title is not None:
            title = title.strip()
            if not title:
                return {
                    "success": False,
                    "error": {
                        "type": "validation_error",
                        "message": "Task title cannot be empty",
                        "details": {},
                    },
                    "message": "The task title can't be empty. Please provide a valid title.",
                }
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

        # Fetch task
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "success": False,
                "error": {
                    "type": "not_found",
                    "message": "Task not found",
                    "details": {"task_id": task_id},
                },
                "message": f"I couldn't find task #{task_id} in your list. Maybe it was already deleted?",
            }

        # Update fields
        updated_fields = []
        if title is not None:
            task.title = title
            updated_fields.append("title")

        if description is not None:
            task.description = description.strip() if description else None
            updated_fields.append("description")

        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Generate friendly message
        if len(updated_fields) == 1:
            field_name = updated_fields[0]
            message = f"Got it! I've updated the {field_name} for '{task.title}'."
        else:
            message = f"Got it! I've updated '{task.title}'."

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
            },
            "updated_fields": updated_fields,
            "message": message,
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
            "message": "Oops! I had trouble updating your task. Please try again in a moment.",
        }


# MCP tool schema for registration
UPDATE_TASK_SCHEMA = {
    "name": "update_task",
    "description": "Update a task's title and/or description",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to update",
            },
            "title": {
                "type": "string",
                "description": "Optional new title for the task (max 500 characters)",
                "maxLength": 500,
            },
            "description": {
                "type": "string",
                "description": "Optional new description for the task",
            },
        },
        "required": ["task_id"],
    },
}
