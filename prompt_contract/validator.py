"""Pure stdlib schema validator and contract enforcement engine."""

from __future__ import annotations

from typing import Any, Dict, List


class ContractViolationError(Exception):
    """Raised when a payload violates the prompt contract schema."""

    def __init__(self, errors: List[str]) -> None:
        self.errors = errors
        super().__init__(f"Contract violation ({len(errors)} error{'s' if len(errors) > 1 else ''}): {'; '.join(errors)}")


def validate_payload(
    payload: Dict[str, Any],
    schema: Dict[str, Any],
    allow_extra_properties: bool = False,
) -> bool:
    """Validate a payload against a JSON schema dictionary.
    
    Raises ContractViolationError if any rule is broken.
    Returns True on success.
    """
    if not isinstance(payload, dict):
        raise ContractViolationError(["Payload must be a JSON object (dictionary)"])

    errors: List[str] = []
    props = schema.get("properties", {})
    required = schema.get("required", [])

    # Check required fields
    for req in required:
        if req not in payload:
            errors.append(f"Missing required property: '{req}'")

    # Check for forbidden extra properties
    if not allow_extra_properties:
        for key in payload:
            if key not in props:
                errors.append(f"Unexpected property not declared in schema: '{key}'")

    # Check individual field types and bounds
    for key, val in payload.items():
        if key not in props:
            continue
        spec = props[key]
        expected_type = spec.get("type")

        if val is None:
            if key in required and not spec.get("nullable", False):
                errors.append(f"Property '{key}' cannot be null")
            continue

        if expected_type == "string" and not isinstance(val, str):
            errors.append(f"Property '{key}' must be a string, got {type(val).__name__}")
        elif expected_type == "integer" and (not isinstance(val, int) or isinstance(val, bool)):
            errors.append(f"Property '{key}' must be an integer, got {type(val).__name__}")
        elif expected_type == "number" and (not isinstance(val, (int, float)) or isinstance(val, bool)):
            errors.append(f"Property '{key}' must be a number, got {type(val).__name__}")
        elif expected_type == "boolean" and not isinstance(val, bool):
            errors.append(f"Property '{key}' must be a boolean, got {type(val).__name__}")
        elif expected_type == "array" and not isinstance(val, list):
            errors.append(f"Property '{key}' must be a list/array, got {type(val).__name__}")
        elif expected_type == "object" and not isinstance(val, dict):
            errors.append(f"Property '{key}' must be an object/dict, got {type(val).__name__}")

        # Check enums
        if "enum" in spec and val not in spec["enum"]:
            errors.append(f"Property '{key}' has value '{val}' not in allowed enum {spec['enum']}")

        # Check numerical bounds
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            if "minimum" in spec and val < spec["minimum"]:
                errors.append(f"Property '{key}' value {val} is below minimum {spec['minimum']}")
            if "maximum" in spec and val > spec["maximum"]:
                errors.append(f"Property '{key}' value {val} exceeds maximum {spec['maximum']}")

    if errors:
        raise ContractViolationError(errors)

    return True
