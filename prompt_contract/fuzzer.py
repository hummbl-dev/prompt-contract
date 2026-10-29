"""Property-based schema fuzzer generating adversarial payloads."""

from __future__ import annotations

import copy
from typing import Any, Dict, Generator, List, Tuple


def _generate_valid_baseline(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Construct a minimal valid payload satisfying the schema."""
    props = schema.get("properties", {})
    required = schema.get("required", [])
    payload = {}

    for prop in required:
        info = props.get(prop, {})
        t = info.get("type", "string")
        if info.get("enum"):
            payload[prop] = info["enum"][0]
        elif t == "string":
            payload[prop] = "sample"
        elif t == "integer":
            payload[prop] = info.get("minimum", 1)
        elif t == "number":
            payload[prop] = float(info.get("minimum", 1.0))
        elif t == "boolean":
            payload[prop] = True
        elif t == "array":
            payload[prop] = []
        elif t == "object":
            payload[prop] = {}
        else:
            payload[prop] = "value"
    return payload


def fuzz_schema(schema: Dict[str, Any]) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """Yield tuples of (fuzz_mutation_type, mutated_payload)."""
    base = _generate_valid_baseline(schema)
    props = schema.get("properties", {})
    required = schema.get("required", [])

    # 1. Missing required field
    for req in required:
        mutated = copy.deepcopy(base)
        del mutated[req]
        yield (f"missing_required_{req}", mutated)

    # 2. Type confusion mutations
    for prop, info in props.items():
        if prop not in base:
            continue
        expected_type = info.get("type", "string")
        mutated = copy.deepcopy(base)
        if expected_type in ("integer", "number"):
            mutated[prop] = "not_a_number"
        elif expected_type == "string":
            mutated[prop] = 12345
        elif expected_type == "boolean":
            mutated[prop] = "true"  # String instead of boolean
        elif expected_type == "array":
            mutated[prop] = {"not": "an_array"}
        yield (f"type_confusion_{prop}", mutated)

    # 3. Extra unexpected property injection
    mutated = copy.deepcopy(base)
    mutated["__unexpected_field__"] = "injection_payload"
    yield ("extra_forbidden_property", mutated)

    # 4. Null value injection on non-nullable fields
    for prop in required:
        mutated = copy.deepcopy(base)
        mutated[prop] = None
        yield (f"null_injection_{prop}", mutated)
