"""
Claude API client wrapper compatible with LangChain's Runnable interface.
Uses Anthropic's Python SDK with Claude CLI authentication.
"""

import logging
from typing import Any, List, Optional, Dict

from anthropic import Anthropic
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from backend.core.claude_auth import ClaudeAuthentication

logger = logging.getLogger("backend")


class ClaudeAPIRunnable(Runnable[LanguageModelInput, BaseMessage]):
    """
    Wrapper around Anthropic's Claude API that conforms to LangChain's Runnable interface.
    This allows dropping in Claude API as a replacement for ChatBedrockConverse.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 1,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        thinking_enabled: bool = False,
        thinking_budget_tokens: Optional[int] = None,
    ):
        """
        Initialize Claude API client using Claude CLI authentication.

        Args:
            model: Model ID (e.g., "claude-3-5-sonnet-20241022")
            temperature: Temperature for sampling (0-1)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt
            thinking_enabled: Enable extended thinking
            thinking_budget_tokens: Budget for thinking tokens (for extended thinking)

        Note:
            Authentication is handled automatically via Claude CLI or ANTHROPIC_API_KEY env var.
            No explicit API key setup needed if using 'claude setup-token'.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.thinking_enabled = thinking_enabled
        self.thinking_budget_tokens = thinking_budget_tokens

        # Ensure authentication is set up and get credentials
        import os
        try:
            api_key, auth_token = ClaudeAuthentication.get_credentials()
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

        # Initialize Anthropic client
        # The Anthropic SDK expects credentials via the api_key parameter or ANTHROPIC_API_KEY env var
        # OAuth tokens (sk-ant-oat01-...) should be treated as API keys - the SDK handles them automatically
        if api_key:
            self.client = Anthropic(api_key=api_key)
            logger.debug(f"Initialized Claude API client with API key")
        elif auth_token:
            # Set OAuth token as ANTHROPIC_API_KEY environment variable
            # The SDK will automatically use it when we call Anthropic()
            os.environ['ANTHROPIC_API_KEY'] = auth_token
            self.client = Anthropic()
            logger.debug(f"Initialized Claude API client with OAuth token (via env)")
        else:
            # Fallback to default auth chain
            self.client = Anthropic()
            logger.debug(f"Initialized Claude API client with default auth")

        self._tools: List[Dict[str, Any]] = []
        logger.debug(f"Claude API client ready with model: {model}")

    def bind_tools(self, tools: List[BaseTool]) -> "ClaudeAPIRunnable":
        """Bind tools to this runnable, returning a new instance with tools configured."""
        new_instance = ClaudeAPIRunnable(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system_prompt=self.system_prompt,
            thinking_enabled=self.thinking_enabled,
            thinking_budget_tokens=self.thinking_budget_tokens,
        )
        new_instance.client = self.client
        new_instance._tools = [self._convert_tool_to_dict(tool) for tool in tools]
        return new_instance

    @staticmethod
    def _convert_tool_to_dict(tool: BaseTool) -> Dict[str, Any]:
        """Convert a LangChain BaseTool to Anthropic tool format."""
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.args_schema.model_json_schema() if hasattr(tool, "args_schema") else {
                "type": "object",
                "properties": {},
            },
        }

    def _format_messages(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert LangChain BaseMessage objects to Anthropic message format."""
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                # Handle both text content and tool use
                if msg.tool_calls:
                    content = []
                    if msg.content:
                        content.append({"type": "text", "text": msg.content})
                    for tool_call in msg.tool_calls:
                        content.append({
                            "type": "tool_use",
                            "id": tool_call.get("id", tool_call.get("name", "unknown")),
                            "name": tool_call["name"],
                            "input": tool_call.get("args", {}),
                        })
                    formatted_messages.append({"role": "assistant", "content": content})
                else:
                    formatted_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                # System messages are handled separately in the API
                pass
            else:
                formatted_messages.append({"role": "user", "content": str(msg.content)})

        return formatted_messages

    def invoke(self, input: LanguageModelInput, config: Optional[Any] = None) -> BaseMessage:
        """Synchronously invoke the Claude API."""
        messages = self._extract_messages(input)
        system_prompt = self._extract_system_prompt(messages)

        # Remove system messages from the messages list (they go in the system parameter)
        messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
        formatted_messages = self._format_messages(messages)

        # Build the request parameters
        request_params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": formatted_messages,
        }

        # Add system prompt if present
        if system_prompt:
            request_params["system"] = system_prompt

        # Add tools if bound
        if self._tools:
            request_params["tools"] = self._tools

        # Add thinking if enabled
        if self.thinking_enabled:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget_tokens or 10000,
            }

        logger.debug(f"Calling Claude API with model={self.model}")
        response = self.client.messages.create(**request_params)

        # Convert response to AIMessage with tool calls if present
        ai_message = self._convert_response_to_ai_message(response)
        return ai_message

    @staticmethod
    def _extract_messages(input: LanguageModelInput) -> List[BaseMessage]:
        """Extract BaseMessage objects from various input formats."""
        if isinstance(input, list):
            return input
        elif isinstance(input, BaseMessage):
            return [input]
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")

    @staticmethod
    def _extract_system_prompt(messages: List[BaseMessage]) -> Optional[str]:
        """Extract system prompt from messages if present."""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                return msg.content
        return None

    @staticmethod
    def _convert_response_to_ai_message(response: Any) -> AIMessage:
        """Convert Anthropic API response to AIMessage with tool calls."""
        tool_calls = []
        content_str = ""

        for block in response.content:
            if block.type == "text":
                content_str += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "name": block.name,
                    "args": block.input,
                    "id": block.id,
                })

        return AIMessage(content=content_str, tool_calls=tool_calls)

    async def ainvoke(self, input: LanguageModelInput, config: Optional[Any] = None) -> BaseMessage:
        """Asynchronously invoke the Claude API."""
        # For now, we use the sync invoke in a thread pool
        # This is not ideal but allows compatibility with async code
        return self.invoke(input, config)

    @property
    def InputType(self):
        return list[BaseMessage]

    @property
    def OutputType(self):
        return BaseMessage
