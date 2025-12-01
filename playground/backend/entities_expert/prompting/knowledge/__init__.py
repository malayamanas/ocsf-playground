import json

from typing import List

from backend.core.ocsf.ocsf_schemas import make_get_ocsf_event_schema, make_get_ocsf_object_schemas, PrintableOcsfEvent, PrintableOcsfObject
from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.core.ocsf.ocsf_schema_v1_1_0 import OCSF_EVENT_CLASSES as ocsf_events_V1_1_0, OCSF_SCHEMA as v1_1_0_schema
from backend.core.ocsf.schema_loader import get_ocsf_schema, get_event_classes


def get_ocsf_event_class_knowledge(ocsf_version: OcsfVersion, ocsf_event_name: str) -> str:
    """Get knowledge about a specific OCSF event class for a given version."""
    # Use pre-generated data for v1.1.0 for backward compatibility
    if ocsf_version == OcsfVersion.V1_1_0:
        event_details = next(
            event for event in ocsf_events_V1_1_0 if event["event_name"] == ocsf_event_name
        )
        return json.dumps(event_details, indent=4)

    # For other versions, get event details dynamically
    try:
        event_classes = get_event_classes(ocsf_version)
        event_details = next(
            (event for event in event_classes if event["event_name"] == ocsf_event_name),
            None
        )

        if event_details:
            return json.dumps(event_details, indent=4)

        return f"Event class '{ocsf_event_name}' not found in OCSF version {ocsf_version.value}"

    except Exception as e:
        return f"Error loading event class knowledge: {str(e)}"


def get_ocsf_event_schema(ocsf_version: OcsfVersion, event_name: str, paths: List[str]) -> PrintableOcsfEvent:
    """Get the OCSF event schema for a specific version."""
    # Use pre-loaded schema for v1.1.0 for backward compatibility and performance
    if ocsf_version == OcsfVersion.V1_1_0:
        return make_get_ocsf_event_schema(v1_1_0_schema)(event_name, paths)

    # For other versions, load schema dynamically
    try:
        schema = get_ocsf_schema(ocsf_version)
        return make_get_ocsf_event_schema(schema)(event_name, paths)
    except Exception as e:
        print(f"Error loading OCSF event schema for version {ocsf_version.value}: {str(e)}")
        return None


def get_ocsf_object_schemas(ocsf_version: OcsfVersion, category_name: str, paths: List[str]) -> List[PrintableOcsfObject]:
    """Get the OCSF object schemas for a specific version."""
    # Use pre-loaded schema for v1.1.0 for backward compatibility and performance
    if ocsf_version == OcsfVersion.V1_1_0:
        return make_get_ocsf_object_schemas(v1_1_0_schema)(category_name, paths)

    # For other versions, load schema dynamically
    try:
        schema = get_ocsf_schema(ocsf_version)
        return make_get_ocsf_object_schemas(schema)(category_name, paths)
    except Exception as e:
        print(f"Error loading OCSF object schemas for version {ocsf_version.value}: {str(e)}")
        return []