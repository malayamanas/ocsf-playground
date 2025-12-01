"""
Dynamic OCSF Schema Loader

This module provides functionality to load OCSF schemas for different versions dynamically.
It uses the ocsf-lib-py package to fetch schemas from the OCSF API and caches them for performance.
"""

from typing import Dict, List
from ocsf.util import get_schema
from ocsf.schema import OcsfSchema

from backend.core.ocsf.ocsf_versions import OcsfVersion

# Global cache for loaded schemas
_schema_cache: Dict[str, OcsfSchema] = {}


def get_ocsf_schema(version: OcsfVersion) -> OcsfSchema:
    """
    Load an OCSF schema for the specified version.

    Args:
        version: The OCSF version enum to load

    Returns:
        OcsfSchema object for the requested version

    Raises:
        ValueError: If the schema cannot be loaded
    """
    version_string = version.value

    # Check cache first
    if version_string in _schema_cache:
        return _schema_cache[version_string]

    try:
        # Load schema using ocsf-lib-py
        schema = get_schema(version_string)

        # Cache it
        _schema_cache[version_string] = schema

        return schema
    except Exception as e:
        raise ValueError(f"Failed to load OCSF schema for version {version_string}: {str(e)}")


def get_event_classes(version: OcsfVersion) -> List[Dict[str, str]]:
    """
    Get all event classes for a specific OCSF version.

    Args:
        version: The OCSF version enum

    Returns:
        List of dicts containing event_name, event_id, and event_details
    """
    schema = get_ocsf_schema(version)

    event_classes = []
    for class_uid, event_class in schema.classes.items():
        event_classes.append({
            "event_name": event_class.caption,
            "event_id": str(event_class.uid),
            "event_details": event_class.description or f"Event class for {event_class.caption}"
        })

    # Sort by event_id for consistency
    event_classes.sort(key=lambda x: int(x["event_id"]))

    return event_classes


def clear_schema_cache(version: OcsfVersion = None):
    """
    Clear the schema cache for a specific version or all versions.

    Args:
        version: Optional version to clear. If None, clears all cached schemas.
    """
    global _schema_cache

    if version is None:
        _schema_cache.clear()
    else:
        _schema_cache.pop(version.value, None)


def preload_schemas():
    """
    Preload schemas for all supported OCSF versions.
    Useful for warming up the cache at application startup.
    """
    for version in OcsfVersion:
        try:
            get_ocsf_schema(version)
            print(f"Preloaded OCSF schema version {version.value}")
        except Exception as e:
            print(f"Warning: Could not preload OCSF schema {version.value}: {str(e)}")
