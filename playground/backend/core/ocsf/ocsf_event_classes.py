"""
OCSF Event Classes

This module provides dynamic event class enums for different OCSF versions.
Event classes are loaded from schemas and cached for performance.
"""

from enum import Enum
import re
from typing import Dict, Type

from backend.core.ocsf.ocsf_versions import OcsfVersion
from backend.core.ocsf.ocsf_schema_v1_1_0 import OCSF_EVENT_CLASSES as ocsf_events_V1_1_0


# Create a custom Enum class that can extract name and ID
class OcsfEventClassEnum(Enum):
    def get_event_name(self):
        """Extract the event name from the value"""
        # Value format is "Event Name (ID)"
        return re.match(r"(.+) \(\d+\)", self.value).group(1)

    def get_event_id(self):
        """Extract the event ID from the value"""
        # Value format is "Event Name (ID)"
        return re.search(r"\((\d+)\)", self.value).group(1)


# Cache for dynamically created enums
_event_class_enum_cache: Dict[str, Type[OcsfEventClassEnum]] = {}


def get_event_class_enum(version: OcsfVersion) -> Type[OcsfEventClassEnum]:
    """
    Get the event class enum for a specific OCSF version.

    Args:
        version: The OCSF version

    Returns:
        Event class enum type for the specified version
    """
    # Check cache first
    if version.value in _event_class_enum_cache:
        return _event_class_enum_cache[version.value]

    # For v1.1.0, use the pre-generated enum for backward compatibility
    if version == OcsfVersion.V1_1_0:
        return OcsfEventClassesV1_1_0

    # For other versions, dynamically create the enum from the schema
    try:
        from backend.core.ocsf.schema_loader import get_event_classes

        event_classes = get_event_classes(version)

        # Prepare the enum members dictionary
        members = {
            f"{event_class['event_name']} {event_class['event_id']}".upper().replace(" ", "_").replace("-", "_"):
            f"{event_class['event_name']} ({event_class['event_id']})"
            for event_class in event_classes
        }

        # Create the enum class
        enum_name = f"OcsfEventClasses_{version.get_url_safe_name()}"
        event_enum = OcsfEventClassEnum(
            enum_name,
            members,
            module=__name__,
        )

        # Cache it
        _event_class_enum_cache[version.value] = event_enum

        return event_enum

    except Exception as e:
        raise ValueError(f"Failed to create event class enum for version {version.value}: {str(e)}")


# Dynamically create the enum members for OCSF categories based on the master list (v1.1.0)
# Prepare the enum members dictionary
members = {
    f"{event_class['event_name']} {event_class['event_id']}".upper().replace(" ", "_").replace("-", "_"):
    f"{event_class['event_name']} ({event_class['event_id']})"
    for event_class in ocsf_events_V1_1_0
}

# Create the enum class with all members at once, using the custom base class
OcsfEventClassesV1_1_0 = OcsfEventClassEnum(
    "OcsfEventClassesV1_1_0",
    members,
    module=__name__,  # Important to make the enum picklable
)