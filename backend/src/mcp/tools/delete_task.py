"""MCP tool for deleting a task."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def delete_task(
    session: AsyncSession,
    user_id: UUID,
    task_id: int,
) -> dict:
    """Delete a task from the user's list.

    Args:
        session: Database session.
        user_id: UUID of the user.
        task_id: ID of the task to delete.

    Returns:
        dict: Success response with confirmation.

    Example:
        >>> result = await delete_task(session, user_id, 123)
        >>> print(result["message"])
        "Done! I've removed 'Buy groceries' from your list."
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

        # Save title for confirmation message
        task_title = task.title

        # Delete task
        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "deleted_task_id": task_id,
            "message": f"Done! I've removed '{task_title}' from your list.",
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
            "message": "Oops! I had trouble deleting your task. Please try again in a moment.",
        }


# MCP tool schema for registration
DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Delete a task from the user's todo list",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The ID of the task to delete",
            },
        },
        "required": ["task_id"],
    },
}
