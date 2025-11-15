from dataclasses import dataclass
import logging

from backend.core.claude_api_client import ClaudeAPIRunnable

from backend.regex_expert.parameters import RegexFlavor
from backend.regex_expert.prompting import get_system_prompt_factory
from backend.regex_expert.tool_def import get_tool_bundle
from backend.regex_expert.task_def import RegexTask

from backend.core.experts import Expert, invoke_expert


logger = logging.getLogger("backend")


def get_regex_expert(regex_flavor: RegexFlavor) -> Expert:
    logger.info(f"Building expert for: {regex_flavor}")

    # Get the tool bundle for the given transform language
    tool_bundle = get_tool_bundle(regex_flavor)

    # Define our Claude API LLM and attach the tools to it
    llm = ClaudeAPIRunnable(
        model="claude-3-5-sonnet-20241022",
        temperature=0,  # Suitable for straightforward, practical code generation
        max_tokens=16000,
        thinking_enabled=False
    )
    llm_w_tools = llm.bind_tools(tool_bundle.to_list())

    return Expert(
        llm=llm_w_tools,
        system_prompt_factory=get_system_prompt_factory(
            regex_flavor=regex_flavor
        ),
        tools=tool_bundle
    )

def invoke_regex_expert(expert: Expert, task: RegexTask) -> RegexTask:
    logger.info(f"Invoking the Regex Expert for task_id: {task.task_id}")
    invoke_expert(expert, task)
    logger.info(f"Regex created for task_id: {task.task_id}")

    return task
