# prompt-contract

> Compile-time and runtime typecheckers, schema fuzzers, and contract tests for LLM prompts and tool calls.

[![CI](https://github.com/hummbl-dev/prompt-contract/actions/workflows/ci.yml/badge.svg)](https://github.com/hummbl-dev/prompt-contract/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

`prompt-contract` eliminates prompt drift and structured output schema breakage in AI agent workflows. It compiles JSON Schema specifications into rigid prompt rules and provides property-based adversarial fuzzing without requiring external dependencies or live LLM API keys.

---

## Features

- **Zero-Dependency Core**: 100% Python 3.11+ standard library.
- **Prompt Compiler**: Converts JSON Schemas into clear, unambiguous system prompt rule blocks with exact types, bounds, and enum constraints.
- **Negative Property Fuzzer**: Automatically generates type-confusion mutations, missing required fields, and unexpected property injection attacks to verify your agent tool handlers.
- **Offline Trace Verification**: Test agent trace histories and recorded outputs in CI/CD without burning API tokens.

---

## Installation

```bash
pip install git+https://github.com/hummbl-dev/prompt-contract.git
```

---

## Quickstart

### 1. Compile Schema to Prompt Instructions
```bash
prompt-contract compile --schema weather_schema.json
```

Output:
```markdown
### Output Contract
You MUST return a valid JSON object strictly complying with the following schema rules:

- `city` (MANDATORY, type: `string`): City name
- `is_raining` (MANDATORY, type: `boolean`)
- `temperature_c` (MANDATORY, type: `number`) (Bounds: >= -90.0, <= 60.0)
- `condition` (OPTIONAL, type: `string`). Allowed values: ['sunny', 'cloudy', 'rainy']

**Strict Constraints**:
1. Do NOT include markdown code fences or explanatory prose around the JSON.
2. Extra unspecified properties are FORBIDDEN.
3. Every mandatory field MUST be present with the exact specified type.
```

### 2. Verify Output Payload
```bash
prompt-contract verify --schema weather_schema.json --payload output.json
```

### 3. Generate Adversarial Fuzz Tests
```bash
prompt-contract fuzz --schema weather_schema.json -n 5
```

---

## Python API

```python
from prompt_contract import compile_prompt_contract, validate_payload, ContractViolationError

schema = {
    "type": "object",
    "required": ["action", "status"],
    "properties": {
        "action": {"type": "string"},
        "status": {"type": "string", "enum": ["ok", "error"]}
    }
}

# Compile prompt
prompt_instructions = compile_prompt_contract(schema)

# Validate response
try:
    validate_payload({"action": "deploy", "status": "ok"}, schema)
    print("Valid!")
except ContractViolationError as e:
    print(f"Contract broken: {e.errors}")
```

---

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
