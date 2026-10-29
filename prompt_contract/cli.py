"""CLI interface for prompt-contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from prompt_contract import __version__
from prompt_contract.compiler import compile_prompt_contract
from prompt_contract.fuzzer import fuzz_schema
from prompt_contract.validator import ContractViolationError, validate_payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prompt-contract",
        description="Compile-time and runtime typecheckers and fuzzers for LLM prompts and tool calls.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: compile
    compile_p = subparsers.add_parser("compile", help="Compile JSON Schema into prompt rule markdown")
    compile_p.add_argument("-s", "--schema", required=True, help="Path to JSON Schema file")
    compile_p.add_argument("-t", "--title", default="Output Contract", help="Section title")

    # Subcommand: verify
    verify_p = subparsers.add_parser("verify", help="Validate a JSON payload or log against a schema")
    verify_p.add_argument("-s", "--schema", required=True, help="Path to JSON Schema file")
    verify_p.add_argument("-p", "--payload", required=True, help="Path to JSON payload file")
    verify_p.add_argument("--allow-extra", action="store_true", help="Allow undeclared extra properties")

    # Subcommand: fuzz
    fuzz_p = subparsers.add_parser("fuzz", help="Generate adversarial negative test cases for a schema")
    fuzz_p.add_argument("-s", "--schema", required=True, help="Path to JSON Schema file")
    fuzz_p.add_argument("-n", "--count", type=int, default=10, help="Max test cases to output")

    args = parser.parse_args(argv)

    try:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading schema: {e}", file=sys.stderr)
        return 1

    if args.command == "compile":
        output = compile_prompt_contract(schema, title=args.title)
        print(output)
        return 0

    elif args.command == "verify":
        try:
            payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
            validate_payload(payload, schema, allow_extra_properties=args.allow_extra)
            print("✓ Payload successfully complies with prompt contract.")
            return 0
        except ContractViolationError as e:
            print(f"✗ CONTRACT VIOLATION:", file=sys.stderr)
            for err in e.errors:
                print(f"  * {err}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Error reading payload: {e}", file=sys.stderr)
            return 1

    elif args.command == "fuzz":
        print(f"Generated negative fuzz cases for {args.schema}:")
        cases = list(fuzz_schema(schema))[: args.count]
        for i, (mutation_type, payload) in enumerate(cases, 1):
            print(f"\n--- Case {i}: [{mutation_type}] ---")
            print(json.dumps(payload, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
