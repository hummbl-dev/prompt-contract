"""prompt-contract: Compile-time and runtime typecheckers and fuzzers for LLM prompts and tool calls."""

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "compile_prompt_contract",
    "fuzz_schema",
    "validate_payload",
    "ContractViolationError",
    "ContractRule",
]

from prompt_contract.compiler import ContractRule, compile_prompt_contract
from prompt_contract.fuzzer import fuzz_schema
from prompt_contract.validator import ContractViolationError, validate_payload
