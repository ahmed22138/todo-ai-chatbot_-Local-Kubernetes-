"""MCP tools for task management."""

from .add_task import ADD_TASK_SCHEMA, add_task
from .complete_task import COMPLETE_TASK_SCHEMA, complete_task
from .delete_task import DELETE_TASK_SCHEMA, delete_task
from .list_tasks import LIST_TASKS_SCHEMA, list_tasks
from .update_task import UPDATE_TASK_SCHEMA, update_task

__all__ = [
    "add_task",
    "ADD_TASK_SCHEMA",
    "list_tasks",
    "LIST_TASKS_SCHEMA",
    "complete_task",
    "COMPLETE_TASK_SCHEMA",
    "update_task",
    "UPDATE_TASK_SCHEMA",
    "delete_task",
    "DELETE_TASK_SCHEMA",
]
