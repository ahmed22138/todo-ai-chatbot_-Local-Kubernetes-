"""OpenAI Assistants SDK integration for natural language task management."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from uuid import UUID

import openai
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import get_mcp_server
from src.models.message import Message, MessageRole

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

logger = logging.getLogger(__name__)


class AgentService:
    """Service for OpenAI Assistants SDK integration with MCP tools."""

    def __init__(self):
        """Initialize agent service with OpenAI Assistants API v2."""
        self.mcp_server = get_mcp_server()
        self.client = openai.AsyncOpenAI(
            api_key=openai.api_key,
            default_headers={"OpenAI-Beta": "assistants=v2"}  # Use v2 API
        )
        self.assistant_id = None  # Will be initialized on first use

        # Instructions for the assistant
        self.instructions = """You are a friendly and helpful task management assistant.
You help users manage their todo tasks through natural language conversation.

You have access to tools that can:
- Add new tasks
- List all tasks or filter by status (incomplete/complete)
- Mark tasks as complete
- Update task details
- Delete tasks

When a user asks about their tasks, use the appropriate tool. Always be friendly,
concise, and provide clear confirmations. Use natural language and avoid technical jargon.

If a user's request is ambiguous, ask for clarification before taking action.
"""

    async def get_or_create_assistant(self) -> str:
        """Get existing assistant or create a new one.

        Returns:
            str: Assistant ID
        """
        if self.assistant_id:
            return self.assistant_id

        try:
            # Get tool schemas from MCP server
            tools = [
                {"type": "function", "function": schema}
                for schema in self.mcp_server.get_tool_schemas()
            ]

            # Create assistant
            assistant = await self.client.beta.assistants.create(
                name="Todo Task Manager",
                instructions=self.instructions,
                model=MODEL_NAME,
                tools=tools,
            )

            self.assistant_id = assistant.id
            logger.info(f"Created new assistant: {self.assistant_id}")
            return self.assistant_id

        except Exception as e:
            logger.error(f"Failed to create assistant: {str(e)}")
            raise

    async def create_thread(self) -> str:
        """Create a new OpenAI thread for conversation.

        Returns:
            str: Thread ID
        """
        try:
            thread = await self.client.beta.threads.create()
            logger.info(f"Created new thread: {thread.id}")
            return thread.id
        except Exception as e:
            logger.error(f"Failed to create thread: {str(e)}")
            raise

    async def invoke_agent(
        self,
        session: AsyncSession,
        user_id: UUID,
        user_message: str,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Invoke the OpenAI Assistant with user message using Assistants API.

        Args:
            session: Database session for tool execution.
            user_id: UUID of the user.
            user_message: The user's message.
            thread_id: Optional thread ID. If None, creates a new thread.

        Returns:
            dict: Agent response with message, thread_id, tool_calls, and metadata.

        Example:
            >>> result = await agent_service.invoke_agent(
            ...     session, user_id, "add buy groceries"
            ... )
            >>> print(result["message"])
            "Great! I've added 'buy groceries' to your task list."
        """
        try:
            # Get or create assistant
            assistant_id = await self.get_or_create_assistant()

            # Create thread if not provided
            if not thread_id:
                thread_id = await self.create_thread()

            # Add message to thread
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )

            # Create and run the assistant
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            # Poll the run until it's complete
            tool_calls_data = []
            tool_results = []

            while True:
                # Wait a bit before checking status
                await asyncio.sleep(0.5)

                # Retrieve the run status
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                logger.info(f"Run status: {run.status}")

                if run.status == "completed":
                    # Get the assistant's messages
                    messages = await self.client.beta.threads.messages.list(
                        thread_id=thread_id,
                        order="desc",
                        limit=1
                    )

                    # Extract the latest assistant message
                    if messages.data:
                        latest_message = messages.data[0]
                        response_text = latest_message.content[0].text.value

                        return {
                            "success": True,
                            "message": response_text,
                            "thread_id": thread_id,
                            "tool_calls": tool_calls_data if tool_calls_data else None,
                            "tool_results": tool_results if tool_results else None,
                        }
                    else:
                        return {
                            "success": True,
                            "message": "I'm here to help! What would you like to do?",
                            "thread_id": thread_id,
                            "tool_calls": None,
                            "tool_results": None,
                        }

                elif run.status == "requires_action":
                    # Handle tool calls
                    tool_outputs = []

                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                        # Execute tool through MCP server
                        result = await self.mcp_server.execute_tool(
                            session=session,
                            user_id=user_id,
                            tool_name=tool_name,
                            parameters=tool_args,
                        )

                        # Store tool call metadata
                        tool_calls_data.append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_args,
                            },
                        })

                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "tool_name": tool_name,
                            "result": result,
                        })

                        # Prepare tool output for submission
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })

                    # Submit tool outputs back to the run
                    run = await self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

                elif run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"Run failed with status: {run.status}")
                    return {
                        "success": False,
                        "message": "I encountered an error processing your request. Please try again.",
                        "thread_id": thread_id,
                        "error": f"Run {run.status}",
                    }

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "success": False,
                "message": "I'm having trouble connecting to my AI service. Please try again in a moment.",
                "error": str(e),
            }

        except Exception as e:
            logger.error(f"Agent invocation error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": "Oops! Something went wrong. Please try again.",
                "error": str(e),
            }

    async def generate_conversation_title(self, first_message: str) -> str:
        """Generate a short, descriptive title for a conversation based on the first message.

        Args:
            first_message: The user's first message in the conversation.

        Returns:
            str: A short title (max 50 characters) describing the conversation topic.

        Example:
            >>> title = await agent_service.generate_conversation_title(
            ...     "I need to buy groceries and plan meals for this week"
            ... )
            >>> print(title)
            "Grocery shopping and meal planning"
        """
        try:
            # Create a prompt to generate a conversation title
            response = await self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a short, descriptive title (max 50 characters) for a conversation based on the user's message. The title should capture the main topic or intent. Return only the title, nothing else.",
                    },
                    {
                        "role": "user",
                        "content": first_message,
                    },
                ],
                max_tokens=20,
                temperature=0.7,
            )

            title = response.choices[0].message.content.strip()

            # Remove quotes if the model added them
            title = title.strip('"\'')

            # Truncate to 50 characters
            if len(title) > 50:
                title = title[:47] + "..."

            return title

        except Exception as e:
            logger.error(f"Failed to generate conversation title: {str(e)}")
            # Return a fallback title
            return "New Conversation"


# Global agent service instance
agent_service = AgentService()


def get_agent_service() -> AgentService:
    """Get the global agent service instance.

    Returns:
        AgentService: The agent service instance.
    """
    return agent_service
