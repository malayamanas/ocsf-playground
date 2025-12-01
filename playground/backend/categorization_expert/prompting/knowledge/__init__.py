from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.core.ocsf.schema_loader import get_event_classes

from backend.categorization_expert.prompting.knowledge.ocsf_v1_1_0 import OCSF_GUIDANCE as v1_1_0_guidance, OCSF_KNOWLEDGE as v1_1_0_knowledge


# Cache for generated knowledge
_knowledge_cache = {}
_guidance_cache = {}


def get_ocsf_guidance(ocsf_version: OcsfVersion) -> str:
    """Get OCSF guidance for a specific version."""
    # Use pre-generated guidance for v1.1.0
    if ocsf_version == OcsfVersion.V1_1_0:
        return v1_1_0_guidance

    # For other versions, generate dynamically
    if ocsf_version.value in _guidance_cache:
        return _guidance_cache[ocsf_version.value]

    # Generate basic guidance for other versions
    guidance = f"""You are an expert in the Open Cybersecurity Schema Framework (OCSF) version {ocsf_version.value}.

Your task is to categorize log entries or data samples into the most appropriate OCSF Event Class.

**Key Guidelines:**
1. Analyze the log entry carefully to understand what type of activity or event it represents
2. Consider the action, actors, objects, and context described in the log
3. Match the log to the OCSF Event Class that best represents the activity
4. Provide a clear rationale explaining why the selected class is the best fit

**OCSF Version:** {ocsf_version.value}
"""

    _guidance_cache[ocsf_version.value] = guidance
    return guidance


def get_ocsf_knowledge(ocsf_version: OcsfVersion) -> str:
    """Get OCSF event class knowledge for a specific version."""
    # Use pre-generated knowledge for v1.1.0
    if ocsf_version == OcsfVersion.V1_1_0:
        return v1_1_0_knowledge

    # Check cache first
    if ocsf_version.value in _knowledge_cache:
        return _knowledge_cache[ocsf_version.value]

    # Generate knowledge dynamically from schema
    try:
        event_classes = get_event_classes(ocsf_version)

        knowledge_parts = [
            f"# OCSF Event Classes - Version {ocsf_version.value}\n",
            "The following OCSF Event Classes are available:\n\n"
        ]

        for event_class in event_classes:
            knowledge_parts.append(
                f"## {event_class['event_name']} (ID: {event_class['event_id']})\n"
                f"{event_class['event_details']}\n\n"
            )

        knowledge = "".join(knowledge_parts)
        _knowledge_cache[ocsf_version.value] = knowledge
        return knowledge

    except Exception as e:
        # Fallback to basic knowledge if dynamic generation fails
        return f"OCSF version {ocsf_version.value} event classes are available. Error loading details: {str(e)}"