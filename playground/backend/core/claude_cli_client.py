"""
Claude CLI client wrapper compatible with LangChain's Runnable interface.
Uses the local Claude CLI binary instead of the Anthropic API.
"""

import json
import logging
import subprocess
from typing import Any, List, Optional, Dict

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

logger = logging.getLogger("backend")


class ClaudeCLIRunnable(Runnable[LanguageModelInput, BaseMessage]):
    """
    Wrapper around Claude CLI that conforms to LangChain's Runnable interface.
    This allows using the Claude CLI as a drop-in replacement for the API client.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 1,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        thinking_enabled: bool = False,
        thinking_budget_tokens: Optional[int] = None,
        cli_path: str = "claude",
    ):
        """
        Initialize Claude CLI client.

        Args:
            model: Model ID (e.g., "claude-3-5-sonnet-20241022")
            temperature: Temperature for sampling (0-1) - not used by CLI
            max_tokens: Maximum tokens in response - not used by CLI
            system_prompt: Optional system prompt
            thinking_enabled: Enable extended thinking - not used by CLI
            thinking_budget_tokens: Budget for thinking tokens - not used by CLI
            cli_path: Path to claude binary (default: "claude" from PATH)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.thinking_enabled = thinking_enabled
        self.thinking_budget_tokens = thinking_budget_tokens
        self.cli_path = cli_path
        self._tools: List[BaseTool] = []
        self._tool_definitions: Dict[str, BaseTool] = {}

        logger.info(f"Initialized Claude CLI client with model: {model}")
        logger.info(f"Using claude binary at: {cli_path}")

    def bind_tools(self, tools: List[BaseTool]) -> "ClaudeCLIRunnable":
        """Bind tools to this runnable, returning a new instance with tools configured."""
        new_instance = ClaudeCLIRunnable(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system_prompt=self.system_prompt,
            thinking_enabled=self.thinking_enabled,
            thinking_budget_tokens=self.thinking_budget_tokens,
            cli_path=self.cli_path,
        )
        new_instance._tools = tools
        # Store tool definitions for response parsing
        new_instance._tool_definitions = {tool.name: tool for tool in tools}
        return new_instance

    def _format_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a simple prompt string."""
        prompt_parts = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                prompt_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                prompt_parts.append(f"Assistant: {msg.content}")
            elif isinstance(msg, SystemMessage):
                # System messages are handled separately
                pass
            else:
                prompt_parts.append(str(msg.content))

        return "\n\n".join(prompt_parts)

    def invoke(self, input: LanguageModelInput, config: Optional[Any] = None) -> BaseMessage:
        """Synchronously invoke the Claude CLI."""
        messages = self._extract_messages(input)
        system_prompt = self._extract_system_prompt(messages) or self.system_prompt

        # Remove system messages from the messages list
        messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
        prompt = self._format_prompt(messages)

        # If tools are bound, add tool instructions to the system prompt
        if self._tools and system_prompt:
            tool_instructions = self._create_tool_instructions()
            system_prompt = f"{system_prompt}\n\n{tool_instructions}"

        # Build the CLI command
        cmd = [
            self.cli_path,
            "--print",  # Non-interactive mode
            "--output-format", "json",  # JSON output for easier parsing
            "--model", self._convert_model_name(self.model),
        ]

        # Add system prompt if present
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        # Add the prompt as the last argument
        cmd.append(prompt)

        logger.debug(f"Calling Claude CLI: {cmd[0]} {cmd[1]} {cmd[2]} {cmd[3]} --model {cmd[5]}")

        try:
            # Call the Claude CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"Claude CLI failed: {error_msg}")
                raise RuntimeError(f"Claude CLI error: {error_msg}")

            # Parse the JSON output
            try:
                output = json.loads(result.stdout)
                # The CLI returns JSON with the response in the 'result' field
                if isinstance(output, dict):
                    response_text = (
                        output.get("result", "") or
                        output.get("text", "") or
                        output.get("content", "") or
                        str(output)
                    )
                else:
                    response_text = str(output)
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw output
                response_text = result.stdout

            logger.debug(f"Claude CLI response: {response_text[:200]}...")

            # If tools are bound, parse the response to extract tool calls
            tool_calls = []
            if self._tools:
                tool_calls = self._parse_tool_calls(response_text)
                logger.debug(f"Extracted {len(tool_calls)} tool calls from response")

            return AIMessage(content=response_text, tool_calls=tool_calls)

        except subprocess.TimeoutExpired:
            logger.error("Claude CLI timed out")
            raise RuntimeError("Claude CLI timed out after 2 minutes")
        except Exception as e:
            logger.error(f"Error calling Claude CLI: {e}")
            raise

    def _convert_model_name(self, model: str) -> str:
        """
        Convert API model names to CLI model aliases.

        The CLI accepts aliases like 'sonnet', 'opus', 'haiku' or full model names.
        """
        # Map common model names to CLI aliases
        model_map = {
            "claude-3-5-sonnet-20241022": "sonnet",
            "claude-3-5-sonnet-20250219": "sonnet",
            "claude-3-7-sonnet-20250219": "sonnet",
            "claude-sonnet-4-5-20250514": "sonnet",  # Claude 4.5 Sonnet
            "claude-4-5-sonnet": "sonnet",
            "claude-3-opus-20240229": "opus",
            "claude-3-haiku-20240307": "haiku",
        }

        # Return the alias if found, otherwise return the full model name
        return model_map.get(model, model)

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

    async def ainvoke(self, input: LanguageModelInput, config: Optional[Any] = None) -> BaseMessage:
        """Asynchronously invoke the Claude CLI."""
        # For now, we use the sync invoke in a thread pool
        # This is not ideal but allows compatibility with async code
        return self.invoke(input, config)

    @property
    def InputType(self):
        return list[BaseMessage]

    @property
    def OutputType(self):
        return BaseMessage

    def _create_example_from_schema(self, schema: Dict[str, Any], definitions: Dict[str, Any] = None) -> Any:
        """Generate an example value from a JSON schema definition."""
        if definitions is None:
            definitions = schema.get("$defs", {})

        schema_type = schema.get("type")

        if schema_type == "string":
            return schema.get("description", "string_value")[:50]
        elif schema_type == "integer":
            return 0
        elif schema_type == "number":
            return 0.0
        elif schema_type == "boolean":
            return False
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            # Resolve $ref if present
            if "$ref" in items_schema:
                ref_path = items_schema["$ref"].split("/")[-1]
                items_schema = definitions.get(ref_path, {})
            example_item = self._create_example_from_schema(items_schema, definitions)
            return [example_item]
        elif schema_type == "object":
            properties = schema.get("properties", {})
            obj = {}
            for prop_name, prop_schema in properties.items():
                # Resolve $ref if present
                if "$ref" in prop_schema:
                    ref_path = prop_schema["$ref"].split("/")[-1]
                    prop_schema = definitions.get(ref_path, {})
                obj[prop_name] = self._create_example_from_schema(prop_schema, definitions)
            return obj
        elif "$ref" in schema:
            ref_path = schema["$ref"].split("/")[-1]
            resolved_schema = definitions.get(ref_path, {})
            return self._create_example_from_schema(resolved_schema, definitions)
        else:
            return "value"

    def _create_tool_instructions(self) -> str:
        """Create instructions for the CLI about available tools."""
        if not self._tools:
            return ""

        tool_descriptions = []
        for tool in self._tools:
            schema = tool.args_schema.model_json_schema() if hasattr(tool, "args_schema") else {}
            properties = schema.get("properties", {})
            definitions = schema.get("$defs", {})

            # Format tool description
            tool_desc = f"\nTool: {tool.name}\nDescription: {tool.description}\n"

            # Generate example JSON structure
            example_args = {}
            for param_name, param_info in properties.items():
                example_args[param_name] = self._create_example_from_schema(param_info, definitions)

            # Format the example JSON
            example_json = json.dumps({
                "tool": tool.name,
                "arguments": example_args
            }, indent=2)

            tool_desc += f"\nExample JSON format:\n```json\n{example_json}\n```\n"

            tool_descriptions.append(tool_desc)

        instructions = (
            "CRITICAL: You MUST respond by calling a tool. "
            "Your response MUST include a JSON code block with the EXACT field names shown in the example. "
            "DO NOT change field names or structure.\n\n"
            "Available tools:\n"
            + "\n".join(tool_descriptions)
        )

        return instructions

    def _parse_tool_calls(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from the CLI response text.
        Looks for JSON blocks containing tool calls.
        """
        import re
        import uuid

        tool_calls = []

        # Look for JSON code blocks
        json_pattern = r'```json\s*(\{[^`]+\})\s*```'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        for match in matches:
            try:
                tool_data = json.loads(match)
                if "tool" in tool_data:
                    tool_call = {
                        "name": tool_data["tool"],
                        "args": tool_data.get("arguments", {}),
                        "id": str(uuid.uuid4()),
                    }
                    tool_calls.append(tool_call)
                    logger.debug(f"Parsed tool call: {tool_call['name']}")
            except json.JSONDecodeError:
                logger.debug(f"Failed to parse JSON block: {match[:100]}")
                continue

        # If no JSON blocks found, try to infer tool call from the first available tool
        if not tool_calls and self._tools:
            logger.warning("No explicit tool call found, attempting to infer from response")
            tool_calls = self._infer_tool_call(response_text)

        return tool_calls

    def _infer_tool_call(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Attempt to infer a tool call from the response text.
        This is a fallback when Claude doesn't use the JSON format.
        """
        import uuid
        import re

        if not self._tools:
            return []

        # Use the first tool (usually there's only one in our experts)
        tool = self._tools[0]
        tool_name = tool.name

        logger.info(f"Inferring tool call for: {tool_name}")
        logger.debug(f"Response text to parse:\n{response_text[:500]}...")

        # Get the parameter schema
        args = {}
        if hasattr(tool, "args_schema"):
            schema = tool.args_schema.model_json_schema()
            properties = schema.get("properties", {})

            # Try to extract parameters from the response text
            for param_name, param_info in properties.items():
                # Look for regex/heuristic values in code blocks
                if param_name in ["value", "new_heuristic", "heuristic"]:
                    # Try multiple patterns to find the regex
                    # Pattern 1: Code blocks with optional language specifier
                    code_pattern = r'```(?:javascript|regex|js)?\s*\n([^\n][^`]*?)\n```'
                    matches = re.findall(code_pattern, response_text, re.DOTALL)

                    # Pattern 2: Look for regex in quotes after "Pattern:" or "Regex:"
                    if not matches:
                        pattern2 = r'(?:Regex|Pattern|Heuristic):\s*[`"\']([^`"\']+)[`"\']'
                        matches = re.findall(pattern2, response_text, re.IGNORECASE)

                    # Pattern 3: Look for anything that looks like a regex (starts with ^, contains special chars)
                    if not matches:
                        pattern3 = r'`([^\`]*(?:\^|\$|\\d|\\w|\\s|\[|\]|\(|\))[^\`]*)`'
                        matches = re.findall(pattern3, response_text)

                    if matches:
                        # Take the first non-empty match
                        regex_value = next((m.strip() for m in matches if m.strip()), None)
                        if regex_value:
                            args[param_name] = regex_value
                            logger.info(f"Extracted regex: {regex_value[:50]}...")

                # Look for rationale/reasoning
                elif param_name in ["rationale", "reasoning"]:
                    # Extract "Rationale:" section or use full response minus code blocks
                    rationale_pattern = r'\*\*Rationale:\*\*\s*\n(.*?)(?:\n\n|$)'
                    matches = re.findall(rationale_pattern, response_text, re.DOTALL | re.IGNORECASE)
                    if matches:
                        args[param_name] = matches[0].strip()
                    else:
                        # Use response text with code blocks removed
                        rationale = re.sub(r'```[^`]*```', '', response_text)
                        args[param_name] = rationale.strip()

                # Look for OCSF categories
                elif param_name in ["ocsf_category", "ocsf_event_name"]:
                    # Look for patterns like "OCSF Category: X" or mentions of event classes
                    category_pattern = r'(?:category|class|event):\s*([^\n]+)'
                    matches = re.findall(category_pattern, response_text, re.IGNORECASE)
                    if matches:
                        args[param_name] = matches[0].strip()

        if args:
            # Check if all required parameters were extracted
            required_params = []
            if hasattr(tool, "args_schema"):
                schema = tool.args_schema.model_json_schema()
                required_params = schema.get("required", [])

            missing_params = [p for p in required_params if p not in args]
            if missing_params:
                logger.warning(f"Missing required parameters: {missing_params}")
                logger.warning(f"Extracted args: {args}")
                logger.warning(f"Full response:\n{response_text}")
                return []

            tool_call = {
                "name": tool_name,
                "args": args,
                "id": str(uuid.uuid4()),
            }
            logger.info(f"Inferred tool call: {tool_name} with args: {list(args.keys())}")
            return [tool_call]

        logger.warning(f"No arguments extracted from response for tool: {tool_name}")
        return []
