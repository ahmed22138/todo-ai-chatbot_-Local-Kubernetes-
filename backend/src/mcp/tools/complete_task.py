"""MCP tool for completing a task."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task, TaskStatus


async def complete_task(
    session: AsyncSession,
    user_id: UUID,
    task_id: int,
) -> dict:
    """Mark a task as complete.

    Args:
        session: Database session.
        user_id: UUID of the user.
        task_id: ID of the task to complete.

    Returns:
        dict: Success response with congratulatory message.

    Example:
        >>> result = await complete_task(session, user_id, 123)
        >>> print(result["message"])
        "Awesome! I've marked 'Buy groceries' as complete."
    """
    try:
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

        # Check if already complete
        if task.status == TaskStatus.COMPLETE:
            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                },
                "message": f"'{task.title}' is already marked as complete!",
            }

        # Mark as complete
        task.status = TaskStatus.COMPLETE
        task.completed_at = datetime.utcnow()

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "completed_at": task.completed_at.isoformat(),
            },
            "message": f"Awesome! I've marked '{task.title}' as complete. 🎉",
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
COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as complete",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to mark as complete",
            },
        },
        "required": ["task_id"],
    },
}
