"""Unit tests for prompt-contract."""

import unittest
from prompt_contract.compiler import compile_prompt_contract
from prompt_contract.fuzzer import fuzz_schema
from prompt_contract.validator import ContractViolationError, validate_payload


class TestPromptContract(unittest.TestCase):
    def setUp(self):
        self.sample_schema = {
            "title": "WeatherResponse",
            "type": "object",
            "required": ["city", "temperature_c", "is_raining"],
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "temperature_c": {"type": "number", "minimum": -90.0, "maximum": 60.0},
                "is_raining": {"type": "boolean"},
                "condition": {"type": "string", "enum": ["sunny", "cloudy", "rainy"]},
            },
        }

    def test_compile_prompt_contract(self):
        compiled = compile_prompt_contract(self.sample_schema, title="Weather Agent Contract")
        self.assertIn("### Weather Agent Contract", compiled)
        self.assertIn("- `city` (MANDATORY, type: `string`): City name", compiled)
        self.assertIn(">= -90.0", compiled)
        self.assertIn("<= 60.0", compiled)
        self.assertIn("Allowed values: ['sunny', 'cloudy', 'rainy']", compiled)

    def test_validate_valid_payload(self):
        valid_payload = {
            "city": "Atlanta",
            "temperature_c": 19.5,
            "is_raining": False,
            "condition": "cloudy",
        }
        self.assertTrue(validate_payload(valid_payload, self.sample_schema))

    def test_missing_required_property(self):
        invalid_payload = {
            "city": "Atlanta",
            "temperature_c": 19.5,
            # missing is_raining
        }
        with self.assertRaises(ContractViolationError) as cm:
            validate_payload(invalid_payload, self.sample_schema)
        self.assertTrue(any("Missing required property: 'is_raining'" in err for err in cm.exception.errors))

    def test_type_confusion_error(self):
        invalid_payload = {
            "city": "Atlanta",
            "temperature_c": "19.5 degrees",  # String instead of number
            "is_raining": False,
        }
        with self.assertRaises(ContractViolationError) as cm:
            validate_payload(invalid_payload, self.sample_schema)
        self.assertTrue(any("must be a number" in err for err in cm.exception.errors))

    def test_forbidden_extra_property(self):
        invalid_payload = {
            "city": "Atlanta",
            "temperature_c": 19.5,
            "is_raining": False,
            "secret_key": "leak_payload",
        }
        with self.assertRaises(ContractViolationError) as cm:
            validate_payload(invalid_payload, self.sample_schema, allow_extra_properties=False)
        self.assertTrue(any("Unexpected property" in err for err in cm.exception.errors))

    def test_fuzzer_generates_invalid_cases(self):
        cases = list(fuzz_schema(self.sample_schema))
        self.assertGreater(len(cases), 3)

        for mutation_type, payload in cases:
            # Every fuzzed payload must be caught by validator
            with self.assertRaises(ContractViolationError, msg=f"Fuzzer case '{mutation_type}' should fail validation"):
                validate_payload(payload, self.sample_schema)


if __name__ == "__main__":
    unittest.main()
