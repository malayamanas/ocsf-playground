from dataclasses import dataclass
import logging
from typing import Any, Callable, Dict

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.runnables import Runnable

from backend.regex_expert.tool_def import ToolBundle
from backend.core.tasks import PlaygroundTask

from backend.core.inference import perform_inference


logger = logging.getLogger("backend")

@dataclass
class Expert:
    llm: Runnable[LanguageModelInput, BaseMessage]
    system_prompt_factory: Callable[[Dict[str, Any]], SystemMessage]
    tools: ToolBundle

class ExpertInvocationError(Exception):
    pass

def invoke_expert(expert: Expert, task: PlaygroundTask) -> PlaygroundTask:
    """
    Invokes the GenAI expert on the given task and updates the passed-in task with the results.
    """

    logger.debug(f"Initial Task: {str(task.to_json())}")

    # Invoke the LLM.  We force the LLM to perform the task by having it make a tool call.  A tool call that conforms
    # to the tool's API will perform the requested task.
    inference_task = task.to_inference_task()
    inference_result = perform_inference(expert.llm, [inference_task])[0]

    logger.debug(f"Inference Result: {str(inference_result.to_json())}")

    # Confirm that the LLM request resulted in a tool call
    if not inference_result.response.tool_calls:
        raise ExpertInvocationError("The LLM did not create a tool call for the task.  Final LLM message: " + inference_result.response.content)

    # Append the LLM response to the context
    task.context.append(inference_result.response)

    # Perform the tool call using the LLM's response to create our final task result
    tool_call = inference_result.response.tool_calls[-1]
    result = expert.tools.task_tool(tool_call["args"])
    task.set_work_item(result)

    # Append the tool call to the context
    task.context.append(
        ToolMessage(
                name=task.get_tool_name(),
                content="Executed the expert task",
                tool_call_id=tool_call["id"]
        )
    )
    
    logger.debug(f"Updated Task: {str(task.to_json())}")

    return task
