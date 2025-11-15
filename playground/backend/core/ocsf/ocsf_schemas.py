from typing import Any, Dict, List, Callable, Tuple

from ocsf.schema import OcsfAttr, OcsfEvent, OcsfObject, OcsfSchema

class PrintableOcsfAttr(OcsfAttr):
    def __init__(self, **kwargs):
        # Initialize parent class with all kwargs
        super().__init__(**kwargs)

    @classmethod
    def from_attr(cls, attr: OcsfAttr):
        """Create a PrintableOcsfAttr from an existing OcsfAttr object."""
        # Create a new instance without calling __init__
        instance = cls.__new__(cls)

        # Copy all attributes from the source attribute
        for attr_name in dir(attr):
            if not attr_name.startswith('_') and not callable(getattr(attr, attr_name, None)):
                try:
                    setattr(instance, attr_name, getattr(attr, attr_name))
                except AttributeError:
                    pass

        # Also copy from __dict__
        for key, value in attr.__dict__.items():
            setattr(instance, key, value)

        return instance

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the attribute to a simplified JSON.
        """
        return {
            "caption": self.caption,
            "description": self.description,
            "type": self.type,
            "type_name": self.type_name,
            "object_type": self.object_type,
            "object_name": self.object_name,
            "requirement": self.requirement,
            "is_array": self.is_array,
            "enum": [
                {
                    "name": enum_name,
                    "value": enum_value.caption,
                    "description": enum_value.description
                }
                for enum_name, enum_value in self.enum.items()
            ] if self.enum else None,
        }


class PrintableOcsfEvent(OcsfEvent):
    def __init__(self, attrs_to_include: List[str] = None, **kwargs):
        # Don't call parent __init__, just copy attributes manually
        # This avoids the positional argument requirement
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Add our custom attribute
        self.attrs_to_include = attrs_to_include

    @classmethod
    def from_event(cls, event: OcsfEvent, attrs_to_include: List[str] = None):
        """Create a PrintableOcsfEvent from an existing OcsfEvent object."""
        # Create a new instance without calling __init__
        instance = cls.__new__(cls)

        # Copy all attributes from the source event
        # Use dir() to get all attributes including those from parent classes
        for attr_name in dir(event):
            # Skip private/magic methods and methods
            if not attr_name.startswith('_') and not callable(getattr(event, attr_name, None)):
                try:
                    setattr(instance, attr_name, getattr(event, attr_name))
                except AttributeError:
                    # Some attributes might be read-only, skip them
                    pass

        # Also copy from __dict__ to ensure we get all instance attributes
        for key, value in event.__dict__.items():
            setattr(instance, key, value)

        # Add our custom attribute
        instance.attrs_to_include = attrs_to_include

        return instance

    def to_dict(self, filter_attributes: bool = False) -> Dict[str, Any]:
        """
        Convert the event to a simplified JSON.  Optionally, only include the attributes specified.
        """

        if filter_attributes and not self.attrs_to_include:
            filtered_attributes = {}
        elif filter_attributes and self.attrs_to_include:
            filtered_attributes = {attr_name: attr for attr_name, attr in self.attributes.items() if attr_name in self.attrs_to_include}
        else:
            filtered_attributes = self.attributes

        return {
            "caption": self.caption,
            "description": self.description,
            "name": self.name,
            "uid": self.uid,
            "attributes": {
                attr_name: PrintableOcsfAttr.from_attr(attr).to_dict()
                for attr_name, attr in filtered_attributes.items()
            }
        }

class PrintableOcsfObject(OcsfObject):
    def __init__(self, include_all_attrs: bool = False, attrs_to_include: List[str] = None, **kwargs):
        # Don't call parent __init__, just set attributes manually
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.include_all_attrs = include_all_attrs
        self.attrs_to_include = attrs_to_include

        if self.include_all_attrs and self.attrs_to_include:
            raise ValueError("Cannot specify to include all attributes and a specific list of attributes to filter out at the same time.")

    @classmethod
    def from_object(cls, obj: OcsfObject, include_all_attrs: bool = False, attrs_to_include: List[str] = None):
        """Create a PrintableOcsfObject from an existing OcsfObject object."""
        # Create a new instance without calling __init__
        instance = cls.__new__(cls)

        # Copy all attributes from the source object
        for attr_name in dir(obj):
            if not attr_name.startswith('_') and not callable(getattr(obj, attr_name, None)):
                try:
                    setattr(instance, attr_name, getattr(obj, attr_name))
                except AttributeError:
                    pass

        # Also copy from __dict__
        for key, value in obj.__dict__.items():
            setattr(instance, key, value)

        # Add our custom attributes
        instance.include_all_attrs = include_all_attrs
        instance.attrs_to_include = attrs_to_include

        if instance.include_all_attrs and instance.attrs_to_include:
            raise ValueError("Cannot specify to include all attributes and a specific list of attributes to filter out at the same time.")

        return instance

    def to_dict(self, filter_attributes: bool = False) -> Dict[str, Any]:
        """
        Convert the object to a simplified JSON.  Optionally, only include the attributes specified.
        """

        if self.include_all_attrs:
            filtered_attributes = self.attributes
        elif filter_attributes and not self.attrs_to_include:
            filtered_attributes = {}
        elif filter_attributes and self.attrs_to_include:
            filtered_attributes = {attr_name: attr for attr_name, attr in self.attributes.items() if attr_name in self.attrs_to_include}
        else:
            filtered_attributes = self.attributes

        return {
            "caption": self.caption,
            "description": self.description,
            "name": self.name,
            "attributes": {
                attr_name: PrintableOcsfAttr.from_attr(attr).to_dict()
                for attr_name, attr in filtered_attributes.items()
            }
        }

def make_get_ocsf_event_schema(schema: OcsfSchema) -> Callable[[str], PrintableOcsfEvent]:
    def get_ocsf_event_schema(event_name: str, paths: List[str]) -> PrintableOcsfEvent:
        """
        Given an OCSF event class name, return the schema for that event class.
        """
        filtered_attributes = [attr_name.split(".")[0] for attr_name in paths]

        # Check if the event class is valid
        event_class = next((e_class for e_class in schema.classes.values() if e_class.caption == event_name), None)
        if event_class is None:
            raise ValueError(f"Invalid event class: {event_name}")

        # Convert the schema to a PrintableOcsfEvent
        # Instead of using __dict__, copy the object directly
        printable_event = PrintableOcsfEvent.from_event(event_class, attrs_to_include=filtered_attributes)

        return printable_event
    
    return get_ocsf_event_schema

def make_get_ocsf_object_schemas(schema: OcsfSchema) -> Callable[[str], List[PrintableOcsfObject]]:
    def get_ocsf_object_schemas(event_name: str, paths: List[str]) -> List[PrintableOcsfObject]:
        """
        Given an OCSF event class name, return the schemas of all objects used by that category.
        """

        # Check if the event class is valid
        event_class = next((e_class for e_class in schema.classes.values() if e_class.caption == event_name), None)
        if event_class is None:
            raise ValueError(f"Invalid event class: {event_name}")

        # Get the objects that the schema uses at the top level
        objects_to_process: List[Tuple[str, OcsfObject]] = []
        for attribute_name, attribute in event_class.attributes.items():
            if attribute.is_object():
                objects_to_process.append((attribute_name, schema.objects[attribute.object_type]))

        # Now, for each object at the top level, get recursively retrieve the objects they use
        returned_objects: Dict[str, OcsfObject] = dict() # Mapping of object type name to object
        relevant_attributes: Dict[str, List[str]] = dict() # Mapping of object type name to list of attributes that are relevant to the paths
        object_was_leaf: Dict[str, bool] = dict() # Mapping of object type name to whether it was a leaf in a path

        while objects_to_process:
            # Get the next object and add it to the final list to return
            next_path, next_object = objects_to_process.pop(0)
            returned_objects[next_object.name] = next_object

            if next_path in paths:
                object_was_leaf[next_object.name] = True

            # If it has any attributes that are also objects, add them to the list if they have not already
            # been processed
            for attribute_name, attribute in next_object.attributes.items():
                attribute_path = f"{next_path}.{attribute_name}"

                # Mark the attribute as relevant if it is a leaf or a transition point in a path
                attribute_is_leaf = attribute_path in paths
                attribute_is_transition = any(path.startswith(attribute_path) for path in paths)
                if attribute_is_leaf or attribute_is_transition:
                    if next_object.name not in relevant_attributes:
                        relevant_attributes[next_object.name] = []
                    if attribute_name not in relevant_attributes[next_object.name]:
                        relevant_attributes[next_object.name].append(attribute_name)

                # If the attribute is an object, process it as well
                if attribute.is_object() and attribute.object_type not in returned_objects:
                    objects_to_process.append((attribute_path, schema.objects[attribute.object_type]))

        # Convert the objects to a list of PrintableOcsfObject, using each object's stored path
        printable_objects = []
        for obj_name, obj in returned_objects.items():
            should_include_all_attrs = obj_name in object_was_leaf # If it was ever a leaf, we want to include all attributes
            filtered_attributes = relevant_attributes.get(obj_name, []) if not should_include_all_attrs else []

            printable_objects.append(PrintableOcsfObject.from_object(obj, include_all_attrs=should_include_all_attrs, attrs_to_include=filtered_attributes))

        return printable_objects
    
    return get_ocsf_object_schemas


