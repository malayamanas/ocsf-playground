import logging

from backend.core.claude_cli_client import ClaudeCLIRunnable

from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.categorization_expert.prompting import get_system_prompt_factory
from backend.categorization_expert.tool_def import get_tool_bundle
from backend.categorization_expert.task_def import CategorizationTask

from backend.core.experts import Expert, invoke_expert


logger = logging.getLogger("backend")


def get_categorization_expert(ocsf_version: OcsfVersion) -> Expert:
    logger.info(f"Building expert for: {ocsf_version}")

    # Get the tool bundle for the given transform language
    tool_bundle = get_tool_bundle(ocsf_version)

    # Define our Claude CLI LLM and attach the tools to it
    llm = ClaudeCLIRunnable(
        model="claude-sonnet-4-5-20250514",
        temperature=0,  # Suitable for straightforward, practical code generation
        max_tokens=16000,
        thinking_enabled=False
    )
    llm_w_tools = llm.bind_tools(tool_bundle.to_list())

    return Expert(
        llm=llm_w_tools,
        system_prompt_factory=get_system_prompt_factory(
            ocsf_version=ocsf_version
        ),
        tools=tool_bundle
    )

def invoke_categorization_expert(expert: Expert, task: CategorizationTask) -> CategorizationTask:
    logger.info(f"Invoking the Categorization Expert for task_id: {task.task_id}")
    invoke_expert(expert, task)
    logger.info(f"Categorization performed for task_id: {task.task_id}")

    return task
