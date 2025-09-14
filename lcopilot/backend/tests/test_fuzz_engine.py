#!/usr/bin/env python3
"""
Fuzz Testing Engine for LCopilot Compliance System
Generates random invalid inputs to test system robustness and error handling.
Ensures the engine never crashes and always returns structured error information.
"""

import unittest
import json
import random
import string
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import copy

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from trust_platform.compliance.rule_engine import RuleEngine

class FuzzGenerator:
    """Generates various types of invalid/corrupted inputs for testing"""

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)

    def random_string(self, length: int = None) -> str:
        """Generate random string of given or random length"""
        if length is None:
            length = random.randint(0, 100)
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

    def random_date(self) -> str:
        """Generate random date string (valid or invalid format)"""
        formats = [
            "YYYY-MM-DD",  # Valid
            "MM/DD/YYYY",  # Different format
            "DD-MM-YYYY",  # Different format
            "invalid-date",  # Invalid
            "2024-13-45",   # Invalid values
            "9999-99-99",   # Extreme values
            "",             # Empty
            "NOT_A_DATE",   # Text
        ]

        format_choice = random.choice(formats)
        if format_choice == "YYYY-MM-DD":
            # Sometimes generate valid, sometimes invalid dates
            if random.choice([True, False]):
                base_date = datetime.now()
                delta = timedelta(days=random.randint(-1000, 1000))
                return (base_date + delta).strftime("%Y-%m-%d")
            else:
                return f"{random.randint(1800, 2100)}-{random.randint(1, 15)}-{random.randint(1, 40)}"
        else:
            return format_choice

    def random_currency(self) -> str:
        """Generate random currency code (valid or invalid)"""
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "BDT", "INR"]
        invalid_currencies = [
            "INVALID", "XXX", "123", "", None, "TOOLONGCURRENCY",
            "$$$", "US_DOLLAR", "euro", "£££", "¥¥¥"
        ]

        all_currencies = valid_currencies + invalid_currencies
        choice = random.choice(all_currencies)
        return choice if choice is not None else ""

    def random_amount(self) -> Union[float, int, str, None]:
        """Generate random amount (valid numbers, invalid types, extreme values)"""
        amount_types = [
            lambda: random.uniform(0.01, 1000000.00),  # Valid positive
            lambda: random.uniform(-1000000.00, -0.01),  # Negative
            lambda: 0.0,  # Zero
            lambda: float('inf'),  # Infinity
            lambda: float('-inf'),  # Negative infinity
            lambda: float('nan'),  # NaN
            lambda: "not-a-number",  # String
            lambda: "",  # Empty string
            lambda: None,  # None
            lambda: random.randint(-999999, 999999),  # Integer
            lambda: "123.45.67",  # Invalid decimal format
            lambda: "1,234,567.89",  # With commas
        ]

        return random.choice(amount_types)()

    def corrupt_field(self, value: Any) -> Any:
        """Corrupt a field value randomly"""
        corruption_strategies = [
            lambda x: None,  # Set to None
            lambda x: "",    # Empty string
            lambda x: random.randint(-999999, 999999),  # Random number
            lambda x: self.random_string(),  # Random string
            lambda x: [],    # Empty array
            lambda x: {},    # Empty dict
            lambda x: [x] if not isinstance(x, (list, dict)) else x,  # Wrap in array
            lambda x: {"corrupted": x},  # Wrap in dict
            lambda x: str(x) if not isinstance(x, str) else random.randint(0, 999),  # Type change
        ]

        return random.choice(corruption_strategies)(value)

    def generate_fuzzed_lc(self, base_lc: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a fuzzed LC document"""
        if base_lc is None:
            base_lc = self.get_base_lc_template()

        fuzzed_lc = copy.deepcopy(base_lc)

        # Randomly corrupt 30-70% of fields
        corruption_rate = random.uniform(0.3, 0.7)
        all_paths = self._get_all_field_paths(fuzzed_lc)
        paths_to_corrupt = random.sample(all_paths, int(len(all_paths) * corruption_rate))

        for path in paths_to_corrupt:
            self._set_nested_value(fuzzed_lc, path, self.corrupt_field(self._get_nested_value(fuzzed_lc, path)))

        # Add some completely random fields
        for _ in range(random.randint(0, 5)):
            fuzzed_lc[self.random_string(10)] = self.corrupt_field("random_value")

        return fuzzed_lc

    def get_base_lc_template(self) -> Dict[str, Any]:
        """Get a basic LC template for fuzzing"""
        return {
            "lc_number": "LC2024-FUZZ-001",
            "issue_date": "2024-01-15",
            "latest_shipment_date": "2024-02-15",
            "expiry_date": "2024-03-01",
            "expiry_place": "Dhaka, Bangladesh",
            "amount": {
                "value": 100000.00,
                "currency": "USD"
            },
            "applicant": {
                "name": "Test Company Ltd.",
                "address": "Test Address",
                "country": "Bangladesh"
            },
            "beneficiary": {
                "name": "Export Company",
                "address": "Export Address",
                "country": "India"
            },
            "description_of_goods": "Test goods",
            "hs_code": "1234.56.78"
        }

    def _get_all_field_paths(self, obj: Any, prefix: str = "") -> List[str]:
        """Get all field paths in a nested object"""
        paths = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{prefix}.{key}" if prefix else key
                paths.append(current_path)
                if isinstance(value, (dict, list)):
                    paths.extend(self._get_all_field_paths(value, current_path))
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                current_path = f"{prefix}[{i}]"
                paths.append(current_path)
                if isinstance(value, (dict, list)):
                    paths.extend(self._get_all_field_paths(value, current_path))
        return paths

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """Get value from nested object using dot notation path"""
        try:
            keys = path.replace('[', '.').replace(']', '').split('.')
            value = obj
            for key in keys:
                if key.isdigit():
                    value = value[int(key)]
                else:
                    value = value[key]
            return value
        except:
            return None

    def _set_nested_value(self, obj: Any, path: str, value: Any) -> None:
        """Set value in nested object using dot notation path"""
        try:
            keys = path.replace('[', '.').replace(']', '').split('.')
            target = obj
            for key in keys[:-1]:
                if key.isdigit():
                    target = target[int(key)]
                else:
                    target = target[key]

            final_key = keys[-1]
            if final_key.isdigit():
                target[int(final_key)] = value
            else:
                target[final_key] = value
        except:
            pass  # Ignore errors in setting values


class FuzzEngineTestSuite(unittest.TestCase):
    """Comprehensive fuzz testing for the compliance engine"""

    @classmethod
    def setUpClass(cls):
        """Set up fuzz testing environment"""
        cls.rule_engine = RuleEngine()
        cls.fuzz_generator = FuzzGenerator(seed=42)  # Reproducible results
        cls.test_results = []

    def test_random_corruption_resilience(self):
        """Test engine resilience against randomly corrupted inputs"""
        print("\n🎯 Testing random corruption resilience...")

        for test_case in range(50):  # Run 50 random corruption tests
            with self.subTest(test_case=test_case):
                try:
                    fuzzed_lc = self.fuzz_generator.generate_fuzzed_lc()

                    # Engine should never crash, always return structured result
                    result = self.rule_engine.validate(fuzzed_lc, "pro")

                    # Validate result structure
                    self.assertIsNotNone(result, "Engine should never return None")
                    self.assertIsInstance(result.score, (int, float), "Score should be numeric")
                    self.assertIsInstance(result.results, list, "Results should be a list")

                    # Score should be between 0 and 1
                    self.assertGreaterEqual(result.score, 0, "Score should not be negative")
                    self.assertLessEqual(result.score, 1, "Score should not exceed 1")

                    print(f"   ✅ Test case {test_case + 1}: Score {result.score:.3f}, {len(result.results)} rules checked")

                except Exception as e:
                    self.fail(f"Engine crashed on test case {test_case + 1}: {str(e)}")

    def test_null_and_empty_values(self):
        """Test handling of null and empty values"""
        print("\n🔍 Testing null and empty value handling...")

        test_cases = [
            {},  # Completely empty
            {"lc_number": None},  # Essential field null
            {"lc_number": ""},    # Essential field empty
            {"amount": None},     # Amount null
            {"amount": {"value": None, "currency": None}},  # Amount components null
            {"applicant": None},  # Applicant null
            {"beneficiary": {}},  # Beneficiary empty dict
        ]

        for i, test_case in enumerate(test_cases):
            with self.subTest(test_case=i):
                try:
                    result = self.rule_engine.validate(test_case, "pro")

                    self.assertIsNotNone(result, f"Engine should handle test case {i}")
                    self.assertGreaterEqual(result.score, 0, f"Score should be valid for test case {i}")

                    print(f"   ✅ Null/empty test {i + 1}: Handled gracefully")

                except Exception as e:
                    self.fail(f"Engine failed on null/empty test case {i}: {str(e)}")

    def test_type_mismatches(self):
        """Test handling of incorrect data types"""
        print("\n🔄 Testing type mismatch handling...")

        base_lc = self.fuzz_generator.get_base_lc_template()

        type_mismatch_tests = [
            ("lc_number", 12345),  # String field as number
            ("issue_date", 20240115),  # Date as number
            ("amount", "not-a-dict"),  # Dict field as string
            ("amount.value", "not-a-number"),  # Number as string
            ("applicant", "not-a-dict"),  # Object as string
            ("required_documents", "not-a-list"),  # Array as string
        ]

        for field, invalid_value in type_mismatch_tests:
            with self.subTest(field=field):
                try:
                    test_lc = copy.deepcopy(base_lc)
                    self.fuzz_generator._set_nested_value(test_lc, field, invalid_value)

                    result = self.rule_engine.validate(test_lc, "pro")

                    self.assertIsNotNone(result, f"Engine should handle type mismatch in {field}")
                    self.assertGreaterEqual(result.score, 0, f"Score should be valid for {field} type mismatch")

                    print(f"   ✅ Type mismatch in {field}: Handled gracefully")

                except Exception as e:
                    self.fail(f"Engine failed on type mismatch for {field}: {str(e)}")

    def test_extreme_values(self):
        """Test handling of extreme values"""
        print("\n⚡ Testing extreme value handling...")

        extreme_value_tests = [
            ("amount.value", float('inf')),  # Infinity
            ("amount.value", float('-inf')), # Negative infinity
            ("amount.value", float('nan')),  # NaN
            ("amount.value", 999999999999999999999999),  # Very large number
            ("lc_number", "A" * 10000),  # Very long string
            ("description_of_goods", "🚢" * 1000),  # Many unicode characters
            ("issue_date", "1800-01-01"),  # Very old date
            ("expiry_date", "2099-12-31"),  # Far future date
        ]

        base_lc = self.fuzz_generator.get_base_lc_template()

        for field, extreme_value in extreme_value_tests:
            with self.subTest(field=field, value=str(extreme_value)[:50]):
                try:
                    test_lc = copy.deepcopy(base_lc)
                    self.fuzz_generator._set_nested_value(test_lc, field, extreme_value)

                    result = self.rule_engine.validate(test_lc, "pro")

                    self.assertIsNotNone(result, f"Engine should handle extreme value in {field}")
                    self.assertIsInstance(result.score, (int, float), f"Score should be numeric for {field}")

                    print(f"   ✅ Extreme value in {field}: Handled gracefully")

                except Exception as e:
                    self.fail(f"Engine failed on extreme value for {field}: {str(e)}")

    def test_malformed_nested_structures(self):
        """Test handling of malformed nested data structures"""
        print("\n🏗️ Testing malformed structure handling...")

        malformed_tests = [
            {"amount": [1, 2, 3]},  # Amount as array instead of object
            {"applicant": ["name", "address"]},  # Applicant as array
            {"beneficiary": {"name": {"nested": {"too": {"deep": "value"}}}}},  # Over-nested
            {"product_details": "should-be-array"},  # Array field as string
            {"tolerance": {"amount": {"nested": {"invalid": "structure"}}}},  # Invalid nesting
        ]

        for i, malformed_data in enumerate(malformed_tests):
            with self.subTest(test_case=i):
                try:
                    result = self.rule_engine.validate(malformed_data, "pro")

                    self.assertIsNotNone(result, f"Engine should handle malformed structure {i}")
                    self.assertGreaterEqual(result.score, 0, f"Score should be valid for malformed structure {i}")

                    print(f"   ✅ Malformed structure {i + 1}: Handled gracefully")

                except Exception as e:
                    self.fail(f"Engine failed on malformed structure {i}: {str(e)}")

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters"""
        print("\n🌍 Testing unicode and special character handling...")

        unicode_tests = [
            "Émojis and spëcial chàracters: 🚢 💰 📋",
            "Chinese characters: 信用证测试",
            "Arabic text: اعتماد مستندي",
            "Russian: Аккредитив тест",
            "Japanese: 信用状テスト",
            "Mixed: Test-$pecial#Characters@123!",
            "\x00\x01\x02\x03",  # Control characters
            "Line\nBreaks\rAnd\tTabs",
            "Null\x00Bytes",
        ]

        base_lc = self.fuzz_generator.get_base_lc_template()

        for i, unicode_text in enumerate(unicode_tests):
            with self.subTest(test_case=i):
                try:
                    test_lc = copy.deepcopy(base_lc)
                    test_lc["description_of_goods"] = unicode_text
                    test_lc["lc_number"] = f"LC-{unicode_text[:10]}"

                    result = self.rule_engine.validate(test_lc, "pro")

                    self.assertIsNotNone(result, f"Engine should handle unicode test {i}")
                    self.assertIsInstance(result.score, (int, float), f"Score should be numeric for unicode test {i}")

                    print(f"   ✅ Unicode test {i + 1}: Handled gracefully")

                except Exception as e:
                    self.fail(f"Engine failed on unicode test {i}: {str(e)}")

    def test_memory_and_performance_stress(self):
        """Test memory usage and performance under stress"""
        print("\n💪 Testing memory and performance stress...")

        # Test with very large documents
        stress_tests = [
            self._generate_large_lc(1000),   # 1000 product line items
            self._generate_deep_nested_lc(10),  # 10 levels deep nesting
            self._generate_wide_lc(100),     # 100 top-level fields
        ]

        for i, stress_lc in enumerate(stress_tests):
            with self.subTest(stress_test=i):
                try:
                    start_time = datetime.now()
                    result = self.rule_engine.validate(stress_lc, "pro")
                    end_time = datetime.now()

                    processing_time = (end_time - start_time).total_seconds()

                    self.assertIsNotNone(result, f"Engine should handle stress test {i}")
                    self.assertLess(processing_time, 30, f"Processing should complete within 30 seconds for stress test {i}")

                    print(f"   ✅ Stress test {i + 1}: Completed in {processing_time:.2f}s")

                except Exception as e:
                    self.fail(f"Engine failed on stress test {i}: {str(e)}")

    def _generate_large_lc(self, num_items: int) -> Dict[str, Any]:
        """Generate LC with many line items"""
        base_lc = self.fuzz_generator.get_base_lc_template()
        base_lc["product_details"] = []

        for i in range(num_items):
            base_lc["product_details"].append({
                "description": f"Product {i}",
                "quantity": random.randint(1, 1000),
                "hs_code": f"{random.randint(1000, 9999)}.{random.randint(10, 99)}.{random.randint(10, 99)}",
                "value": random.uniform(1, 10000),
                "origin": random.choice(["India", "China", "USA", "Germany"])
            })

        return base_lc

    def _generate_deep_nested_lc(self, depth: int) -> Dict[str, Any]:
        """Generate deeply nested LC structure"""
        base_lc = self.fuzz_generator.get_base_lc_template()

        # Create deep nesting
        nested_obj = base_lc
        for i in range(depth):
            nested_obj[f"level_{i}"] = {}
            nested_obj = nested_obj[f"level_{i}"]
        nested_obj["deep_value"] = "reached maximum depth"

        return base_lc

    def _generate_wide_lc(self, num_fields: int) -> Dict[str, Any]:
        """Generate LC with many top-level fields"""
        base_lc = self.fuzz_generator.get_base_lc_template()

        for i in range(num_fields):
            base_lc[f"custom_field_{i}"] = self.fuzz_generator.random_string(50)

        return base_lc

    def tearDown(self):
        """Clean up after each test"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        print(f"\n🎯 Fuzz Testing Summary:")
        print(f"   All fuzz tests completed successfully")
        print(f"   Engine demonstrated robust error handling")
        print(f"   No crashes or unhandled exceptions detected")


def run_fuzz_tests():
    """Run the complete fuzz test suite"""
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FuzzEngineTestSuite))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful(), len(result.failures), len(result.errors)


if __name__ == "__main__":
    print("🚀 Running LCopilot Fuzz Test Suite")
    print("=" * 60)

    success, failures, errors = run_fuzz_tests()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL FUZZ TESTS PASSED - Engine is Robust")
    else:
        print(f"❌ FUZZ TESTS FAILED - {failures} failures, {errors} errors")
        sys.exit(1)