"""MCP tool for listing tasks."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task, TaskStatus


async def list_tasks(
    session: AsyncSession,
    user_id: UUID,
    status: Optional[str] = None,
) -> dict:
    """List tasks for the user, optionally filtered by status.

    Args:
        session: Database session.
        user_id: UUID of the user.
        status: Optional status filter ("incomplete" or "complete").

    Returns:
        dict: Task list with count and friendly message.

    Example:
        >>> result = await list_tasks(session, user_id, status="incomplete")
        >>> print(result["message"])
        "You have 3 incomplete tasks."
    """
    try:
        # Build query
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter if provided
        if status:
            try:
                status_enum = TaskStatus(status.lower())
                query = query.where(Task.status == status_enum)
            except ValueError:
                return {
                    "success": False,
                    "error": {
                        "type": "validation_error",
                        "message": f"Invalid status: {status}",
                        "details": {"valid_values": ["incomplete", "complete"]},
                    },
                    "message": f"I don't recognize the status '{status}'. Try 'incomplete' or 'complete'.",
                }

        # Order by created_at descending (newest first)
        query = query.order_by(Task.created_at.desc())

        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()

        # Format tasks for response
        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }
            for task in tasks
        ]

        # Generate friendly message
        count = len(task_list)
        if count == 0:
            if status == "incomplete":
                message = "You're all caught up! No incomplete tasks."
            elif status == "complete":
                message = "You haven't completed any tasks yet."
            else:
                message = "You don't have any tasks yet. Want to add one?"
        elif count == 1:
            if status == "incomplete":
                message = "You have 1 incomplete task."
            elif status == "complete":
                message = "You've completed 1 task."
            else:
                message = "You have 1 task."
        else:
            if status == "incomplete":
                message = f"You have {count} incomplete tasks."
            elif status == "complete":
                message = f"You've completed {count} tasks."
            else:
                message = f"You have {count} tasks."

        return {
            "success": True,
            "tasks": task_list,
            "count": count,
            "message": message,
        }

    except Exception as e:
        # Database or system error
        return {
            "success": False,
            "error": {
                "type": "system_error",
                "message": f"Database error: {str(e)}",
                "details": {"exception_type": type(e).__name__},
            },
            "message": "Oops! I had trouble fetching your tasks. Please try again in a moment.",
        }


# MCP tool schema for registration
LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": "List the user's tasks, optionally filtered by status",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Optional status filter: 'incomplete' or 'complete'",
                "enum": ["incomplete", "complete"],
            },
        },
        "required": [],
    },
}
