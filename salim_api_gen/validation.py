from typing import Any, Dict
from .exceptions import ValidationError


def validate_schema(data: Any, schema: Dict[str, Any]) -> None:
    """
    Validate data against a JSON schema.
    """
    try:
        import jsonschema
    except ImportError:
        raise ImportError(
            "jsonschema is required for schema validation. Install it with 'pip install jsonschema'."
        )

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ValidationError(f"Schema validation failed: {e}")
