import logging

from backend.core.claude_cli_client import ClaudeCLIRunnable

from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.entities_expert.prompting import get_analyze_system_prompt_factory, get_extract_system_prompt_factory
from backend.entities_expert.tool_def import get_analyze_tool_bundle, get_extract_tool_bundle
from backend.entities_expert.task_def import AnalysisTask, ExtractTask

from backend.core.experts import Expert, invoke_expert


logger = logging.getLogger("backend")


def get_analysis_expert(ocsf_version: OcsfVersion, ocsf_event_name: str) -> Expert:
    logger.info(f"Building expert for: {ocsf_version}")

    tool_bundle = get_analyze_tool_bundle(ocsf_version)

    # Define our Claude CLI LLM with extended thinking enabled
    llm = ClaudeCLIRunnable(
        model="claude-sonnet-4-5-20250514",
        temperature=1,  # Required for extended thinking
        max_tokens=30001,
        thinking_enabled=True,
        thinking_budget_tokens=30000
    )
    llm_w_tools = llm.bind_tools(tool_bundle.to_list())

    return Expert(
        llm=llm_w_tools,
        system_prompt_factory=get_analyze_system_prompt_factory(
            ocsf_version=ocsf_version,
            ocsf_event_name=ocsf_event_name
        ),
        tools=tool_bundle
    )

def invoke_analysis_expert(expert: Expert, task: AnalysisTask) -> AnalysisTask:
    logger.info(f"Invoking the Analysis Expert for task_id: {task.task_id}")
    invoke_expert(expert, task)
    logger.info(f"Analysis performed for task_id: {task.task_id}")

    return task

def get_extraction_expert(ocsf_version: OcsfVersion, ocsf_event_name: str) -> Expert:
    logger.info(f"Building expert for: {ocsf_version}")

    tool_bundle = get_extract_tool_bundle(ocsf_version)

    # Define our Claude CLI LLM and attach the tools to it
    llm = ClaudeCLIRunnable(
        model="claude-sonnet-4-5-20250514",
        temperature=0,  # Good for straightforward, practical code generation
        max_tokens=30000,
        thinking_enabled=False
    )
    llm_w_tools = llm.bind_tools(tool_bundle.to_list())

    return Expert(
        llm=llm_w_tools,
        system_prompt_factory=get_extract_system_prompt_factory(
            ocsf_version=ocsf_version,
            ocsf_event_name=ocsf_event_name
        ),
        tools=tool_bundle
    )

def invoke_extraction_expert(expert: Expert, task: ExtractTask) -> ExtractTask:
    logger.info(f"Invoking the Extraction Expert for task_id: {task.task_id}")
    invoke_expert(expert, task)
    logger.info(f"Extraction performed for task_id: {task.task_id}")

    return task
