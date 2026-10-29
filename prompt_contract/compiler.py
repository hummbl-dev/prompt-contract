"""Compiler for turning JSON Schemas into strict system prompt rule constraints."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ContractRule:
    field_name: str
    field_type: str
    required: bool
    description: str = ""
    enum_values: List[Any] = field(default_factory=list)
    min_value: float | None = None
    max_value: float | None = None

    def to_prompt_clause(self) -> str:
        req_str = "MANDATORY" if self.required else "OPTIONAL"
        clause = f"- `{self.field_name}` ({req_str}, type: `{self.field_type}`)"
        if self.description:
            clause += f": {self.description}"
        if self.enum_values:
            clause += f". Allowed values: {self.enum_values}"
        if self.min_value is not None or self.max_value is not None:
            bounds = []
            if self.min_value is not None:
                bounds.append(f">= {self.min_value}")
            if self.max_value is not None:
                bounds.append(f"<= {self.max_value}")
            clause += f" (Bounds: {', '.join(bounds)})"
        return clause


def compile_prompt_contract(schema: Dict[str, Any], title: str = "Output Contract") -> str:
    """Compile a JSON schema into an unambiguous prompt specification."""
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    rules: List[ContractRule] = []
    for prop_name, prop_def in properties.items():
        rules.append(
            ContractRule(
                field_name=prop_name,
                field_type=prop_def.get("type", "any"),
                required=prop_name in required,
                description=prop_def.get("description", ""),
                enum_values=prop_def.get("enum", []),
                min_value=prop_def.get("minimum"),
                max_value=prop_def.get("maximum"),
            )
        )

    lines = [
        f"### {title}",
        "You MUST return a valid JSON object strictly complying with the following schema rules:",
        "",
    ]
    for r in sorted(rules, key=lambda x: (not x.required, x.field_name)):
        lines.append(r.to_prompt_clause())

    lines.extend([
        "",
        "**Strict Constraints**:",
        "1. Do NOT include markdown code fences or explanatory prose around the JSON.",
        "2. Extra unspecified properties are FORBIDDEN.",
        "3. Every mandatory field MUST be present with the exact specified type.",
    ])

    return "\n".join(lines)
