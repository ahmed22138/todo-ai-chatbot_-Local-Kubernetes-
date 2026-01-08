"""MCP server for task management tools."""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.tools import (
    ADD_TASK_SCHEMA,
    COMPLETE_TASK_SCHEMA,
    DELETE_TASK_SCHEMA,
    LIST_TASKS_SCHEMA,
    UPDATE_TASK_SCHEMA,
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)


class MCPServer:
    """MCP server for exposing task management tools to AI agents.

    This server implements the Model Context Protocol (MCP) to allow
    AI agents to interact with the task management system through
    well-defined tool interfaces.

    The agent never accesses the database directly - all operations
    go through these MCP tools.
    """

    def __init__(self):
        """Initialize MCP server with tool registry."""
        self.tools = {
            "add_task": {
                "handler": add_task,
                "schema": ADD_TASK_SCHEMA,
            },
            "list_tasks": {
                "handler": list_tasks,
                "schema": LIST_TASKS_SCHEMA,
            },
            "complete_task": {
                "handler": complete_task,
                "schema": COMPLETE_TASK_SCHEMA,
            },
            "update_task": {
                "handler": update_task,
                "schema": UPDATE_TASK_SCHEMA,
            },
            "delete_task": {
                "handler": delete_task,
                "schema": DELETE_TASK_SCHEMA,
            },
        }

    def get_tool_schemas(self) -> list[dict]:
        """Get JSON schemas for all registered tools.

        Returns:
            list[dict]: List of tool schemas for OpenAI function calling.

        Example:
            >>> server = MCPServer()
            >>> schemas = server.get_tool_schemas()
            >>> print(len(schemas))
            5
        """
        return [tool["schema"] for tool in self.tools.values()]

    async def execute_tool(
        self,
        session: AsyncSession,
        user_id: UUID,
        tool_name: str,
        parameters: Dict[str, Any],
    ) -> dict:
        """Execute a tool with the given parameters.

        Args:
            session: Database session.
            user_id: UUID of the user making the request.
            tool_name: Name of the tool to execute.
            parameters: Tool parameters from agent.

        Returns:
            dict: Tool execution result.

        Raises:
            ValueError: If tool not found.

        Example:
            >>> result = await server.execute_tool(
            ...     session, user_id, "add_task",
            ...     {"title": "Buy groceries", "description": "Milk, eggs"}
            ... )
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "message": f"I don't know how to use the tool '{tool_name}'.",
            }

        tool = self.tools[tool_name]
        handler = tool["handler"]

        try:
            # All tools accept session and user_id, plus their specific parameters
            result = await handler(session=session, user_id=user_id, **parameters)
            return result
        except TypeError as e:
            return {
                "success": False,
                "error": f"Invalid parameters for {tool_name}: {str(e)}",
                "message": f"Something went wrong with the parameters for '{tool_name}'. Please try again.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "message": f"Oops! Something went wrong while executing '{tool_name}'. Our team has been notified.",
            }

    def list_tools(self) -> list[str]:
        """List all available tool names.

        Returns:
            list[str]: List of tool names.
        """
        return list(self.tools.keys())


# Global MCP server instance
mcp_server = MCPServer()


def get_mcp_server() -> MCPServer:
    """Get the global MCP server instance.

    Returns:
        MCPServer: The MCP server instance.

    Example:
        >>> server = get_mcp_server()
        >>> tools = server.list_tools()
    """
    return mcp_server
