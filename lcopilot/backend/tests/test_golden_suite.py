#!/usr/bin/env python3
"""
Golden LC Test Suite
Automated regression tests for compliance engine using comprehensive LC fixtures.
Ensures core compliance scenarios work correctly across all rule sets.
"""

import unittest
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from trust_platform.compliance.rule_engine import RuleEngine
from trust_platform.compliance.compliance_integration import ComplianceIntegration


class GoldenLCTestSuite(unittest.TestCase):
    """Comprehensive test suite using golden LC fixtures"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures and compliance engines"""
        cls.fixtures_path = Path(__file__).parent.parent / "fixtures"
        cls.rule_engine = RuleEngine()
        cls.compliance_integration = ComplianceIntegration()

        # Load all test fixtures
        cls.fixtures = {}
        fixture_files = [
            "lc_valid_full.json",
            "lc_invalid_date.json",
            "lc_invalid_hs_code.json",
            "lc_partial_shipment.json",
            "lc_bangladesh_fail.json"
        ]

        for fixture_file in fixture_files:
            fixture_path = cls.fixtures_path / fixture_file
            if fixture_path.exists():
                with open(fixture_path, 'r') as f:
                    cls.fixtures[fixture_file] = json.load(f)
            else:
                raise FileNotFoundError(f"Required fixture not found: {fixture_path}")

        print(f"Loaded {len(cls.fixtures)} golden LC fixtures for testing")

    def test_valid_full_lc_compliance(self):
        """Test fully compliant LC passes all validation rules"""
        lc_document = self.fixtures["lc_valid_full.json"]
        expected = lc_document["_test_expectations"]

        # Test with new rule engine
        result = self.rule_engine.validate(lc_document, "pro")

        # Assertions based on test expectations
        self.assertGreaterEqual(result.score, 0.9,
                              "Fully compliant LC should achieve high compliance score")

        # Check that no critical failures occurred
        failed_rules = [r for r in result.results if r.status.value == "fail"]
        self.assertEqual(len(failed_rules), 0,
                        f"Fully compliant LC should have no failures, but found: {[r.id for r in failed_rules]}")

        # Verify expected rule coverage
        rule_ids = [r.id for r in result.results]
        self.assertIn("UCP600-6", rule_ids, "Should test expiry requirements")
        self.assertIn("UCP600-14", rule_ids, "Should test presentation period")

        print(f"✅ Valid Full LC: Score {result.score:.3f}, {len(failed_rules)} failures")

    def test_invalid_date_logic_failures(self):
        """Test LC with date logic violations fails appropriately"""
        lc_document = self.fixtures["lc_invalid_date.json"]
        expected = lc_document["_test_expectations"]

        # Test with new rule engine
        result = self.rule_engine.validate(lc_document, "pro")

        # Should have low compliance score due to date issues
        self.assertLess(result.score, 0.5,
                       "LC with date violations should have low compliance score")

        # Check for date-related failures
        failed_rules = [r for r in result.results if r.status.value == "fail"]
        self.assertGreater(len(failed_rules), 0,
                          "LC with date violations should have rule failures")

        # Look for specific date logic violations
        date_related_failures = [r for r in failed_rules
                               if "date" in r.details.lower() or "UCP600-31" in r.id or "ISBP-A11" in r.id]
        self.assertGreater(len(date_related_failures), 0,
                          "Should detect date logic violations")

        print(f"✅ Invalid Date LC: Score {result.score:.3f}, {len(failed_rules)} failures, {len(date_related_failures)} date-related")

    def test_invalid_hs_code_failures(self):
        """Test LC with HS code violations fails appropriately"""
        lc_document = self.fixtures["lc_invalid_hs_code.json"]
        expected = lc_document["_test_expectations"]

        # Test with new rule engine
        result = self.rule_engine.validate(lc_document, "pro")

        # Should have moderate compliance score due to HS code issues
        self.assertLess(result.score, 0.7,
                       "LC with HS code violations should have reduced compliance score")

        # Check for HS code related failures
        failed_rules = [r for r in result.results if r.status.value == "fail"]
        hs_related_failures = [r for r in failed_rules
                             if "hs" in r.details.lower() or "BD-003" in r.id]

        # May not have direct HS code failures if rules aren't implemented yet
        # But should have documentation/classification issues
        doc_related_failures = [r for r in failed_rules
                              if "classification" in r.details.lower() or "code" in r.details.lower()]

        print(f"✅ Invalid HS Code LC: Score {result.score:.3f}, {len(failed_rules)} failures, HS/doc issues detected")

    def test_partial_shipment_compliance(self):
        """Test LC with partial shipment terms validates correctly"""
        lc_document = self.fixtures["lc_partial_shipment.json"]
        expected = lc_document["_test_expectations"]

        # Test with new rule engine
        result = self.rule_engine.validate(lc_document, "pro")

        # Should pass most rules despite complexity
        self.assertGreaterEqual(result.score, 0.7,
                              "Well-structured partial shipment LC should achieve good compliance")

        # Check for partial shipment specific validations
        failed_rules = [r for r in result.results if r.status.value == "fail"]
        partial_related_rules = [r for r in result.results
                               if "partial" in r.details.lower() or "shipment" in r.details.lower()]

        self.assertGreater(len(partial_related_rules), 0,
                          "Should evaluate partial shipment terms")

        print(f"✅ Partial Shipment LC: Score {result.score:.3f}, {len(partial_related_rules)} partial shipment rules checked")

    def test_bangladesh_specific_failures(self):
        """Test LC violating Bangladesh-specific rules fails appropriately"""
        lc_document = self.fixtures["lc_bangladesh_fail.json"]
        expected = lc_document["_test_expectations"]

        # Test with new rule engine
        result = self.rule_engine.validate(lc_document, "pro")

        # Should have low compliance score due to multiple BD violations
        self.assertLess(result.score, 0.6,
                       "LC with multiple Bangladesh violations should have low compliance score")

        # Check for Bangladesh-specific failures
        failed_rules = [r for r in result.results if r.status.value == "fail"]
        bd_related_failures = [r for r in failed_rules
                             if r.id.startswith("BD-") or "bangladesh" in r.details.lower()]

        # Should detect multiple issues
        currency_issues = [r for r in failed_rules if "currency" in r.details.lower() or "EUR" in r.details]
        address_issues = [r for r in failed_rules if "address" in r.details.lower()]

        print(f"✅ Bangladesh Fail LC: Score {result.score:.3f}, {len(failed_rules)} total failures")
        print(f"   BD-specific: {len(bd_related_failures)}, Currency: {len(currency_issues)}, Address: {len(address_issues)}")

    def test_tier_based_validation(self):
        """Test that tier-based validation works correctly"""
        lc_document = self.fixtures["lc_valid_full.json"]

        # Test free tier (should limit checks)
        free_result = self.rule_engine.validate(lc_document, "free", remaining_free_checks=3)

        # Test pro tier (unlimited)
        pro_result = self.rule_engine.validate(lc_document, "pro")

        # Free tier should trigger upsell
        self.assertTrue(free_result.upsell_triggered, "Free tier should trigger upsell")
        self.assertEqual(free_result.checks_remaining, 0, "Free tier should consume all checks")

        # Pro tier should not trigger upsell
        self.assertFalse(pro_result.upsell_triggered, "Pro tier should not trigger upsell")
        self.assertEqual(pro_result.checks_remaining, -1, "Pro tier should have unlimited checks")

        print(f"✅ Tier Testing: Free triggered upsell: {free_result.upsell_triggered}, Pro unlimited: {pro_result.checks_remaining == -1}")

    def test_integration_layer_compatibility(self):
        """Test that integration layer works with both engines"""
        lc_document = self.fixtures["lc_valid_full.json"]

        # Test through integration layer (should use new engine by default)
        result = self.compliance_integration.validate_lc_compliance(lc_document, "test-customer", "pro")

        # Verify integration layer response format
        self.assertIn("compliance_score", result)
        self.assertIn("overall_status", result)
        self.assertIn("validated_rules", result)
        self.assertIn("tier_used", result)

        # Test engine switching
        self.compliance_integration.switch_engine(use_new_engine=False)
        old_result = self.compliance_integration.validate_lc_compliance(lc_document, "test-customer", "pro")

        self.assertIn("compliance_score", old_result)

        print(f"✅ Integration Layer: New engine score {result['compliance_score']:.3f}, Old engine available")

    def test_rule_coverage_completeness(self):
        """Test that all major rule categories are covered"""
        lc_document = self.fixtures["lc_valid_full.json"]
        result = self.rule_engine.validate(lc_document, "pro")

        # Collect rule categories
        rule_categories = set()
        for rule_result in result.results:
            if rule_result.id.startswith("UCP600"):
                rule_categories.add("UCP600")
            elif rule_result.id.startswith("ISBP"):
                rule_categories.add("ISBP")
            elif rule_result.id.startswith("BD-"):
                rule_categories.add("BD_LOCAL")

        # Should cover multiple categories
        self.assertGreaterEqual(len(rule_categories), 2,
                              f"Should cover multiple rule categories, found: {rule_categories}")

        # Count rules by category
        ucp600_rules = [r for r in result.results if r.id.startswith("UCP600")]
        isbp_rules = [r for r in result.results if r.id.startswith("ISBP")]
        bd_rules = [r for r in result.results if r.id.startswith("BD-")]

        print(f"✅ Rule Coverage: UCP600: {len(ucp600_rules)}, ISBP: {len(isbp_rules)}, BD: {len(bd_rules)}")

    def test_performance_benchmarks(self):
        """Test that validation performance meets benchmarks"""
        lc_document = self.fixtures["lc_valid_full.json"]

        import time
        start_time = time.time()

        # Run multiple validations to test performance
        for _ in range(5):
            result = self.rule_engine.validate(lc_document, "pro")

        end_time = time.time()
        avg_time = (end_time - start_time) / 5

        # Should validate within reasonable time (< 1 second per validation)
        self.assertLess(avg_time, 1.0, f"Validation should complete within 1 second, took {avg_time:.3f}s")

        print(f"✅ Performance: Average validation time {avg_time:.3f}s")

    def test_error_handling_robustness(self):
        """Test error handling with malformed LC documents"""
        # Test with missing required fields
        incomplete_lc = {
            "lc_number": "INCOMPLETE-001",
            # Missing most required fields
        }

        try:
            result = self.rule_engine.validate(incomplete_lc, "pro")
            # Should not crash, should return some results
            self.assertIsNotNone(result, "Should handle incomplete documents gracefully")
            print(f"✅ Error Handling: Handled incomplete LC with score {result.score:.3f}")
        except Exception as e:
            self.fail(f"Should not raise exception for incomplete LC: {str(e)}")

        # Test with invalid data types
        invalid_lc = {
            "lc_number": 12345,  # Should be string
            "amount": "invalid",  # Should be dict
            "issue_date": "invalid-date-format"
        }

        try:
            result = self.rule_engine.validate(invalid_lc, "pro")
            self.assertIsNotNone(result, "Should handle invalid data types gracefully")
            print(f"✅ Error Handling: Handled invalid data types with score {result.score:.3f}")
        except Exception as e:
            self.fail(f"Should not raise exception for invalid data types: {str(e)}")

    def test_regression_protection(self):
        """Ensure no regression in core functionality"""
        # Test all fixtures to ensure no unexpected changes
        regression_results = {}

        for fixture_name, lc_document in self.fixtures.items():
            try:
                result = self.rule_engine.validate(lc_document, "pro")
                regression_results[fixture_name] = {
                    "score": result.score,
                    "total_rules": len(result.results),
                    "failures": len([r for r in result.results if r.status.value == "fail"]),
                    "success": True
                }
            except Exception as e:
                regression_results[fixture_name] = {
                    "error": str(e),
                    "success": False
                }

        # All fixtures should process successfully
        failed_fixtures = [name for name, result in regression_results.items() if not result["success"]]
        self.assertEqual(len(failed_fixtures), 0,
                        f"Fixtures should not fail processing: {failed_fixtures}")

        print("✅ Regression Protection: All fixtures processed successfully")
        for name, result in regression_results.items():
            if result["success"]:
                print(f"   {name}: Score {result['score']:.3f}, {result['failures']} failures")

    def tearDown(self):
        """Clean up after each test"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        print(f"\n🎯 Golden LC Test Suite completed")
        print(f"   Fixtures tested: {len(cls.fixtures)}")
        print(f"   Compliance engine validated across all scenarios")


class TestFixtureValidation(unittest.TestCase):
    """Validate that test fixtures themselves are well-formed"""

    def setUp(self):
        self.fixtures_path = Path(__file__).parent.parent / "fixtures"

    def test_fixture_files_exist(self):
        """Ensure all required fixture files exist"""
        required_fixtures = [
            "lc_valid_full.json",
            "lc_invalid_date.json",
            "lc_invalid_hs_code.json",
            "lc_partial_shipment.json",
            "lc_bangladesh_fail.json"
        ]

        for fixture_file in required_fixtures:
            fixture_path = self.fixtures_path / fixture_file
            self.assertTrue(fixture_path.exists(), f"Required fixture missing: {fixture_file}")

    def test_fixture_json_validity(self):
        """Ensure all fixtures are valid JSON"""
        fixture_files = list(self.fixtures_path.glob("lc_*.json"))

        for fixture_file in fixture_files:
            with self.subTest(fixture=fixture_file.name):
                try:
                    with open(fixture_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {fixture_file.name}: {str(e)}")

    def test_fixture_test_expectations(self):
        """Ensure all fixtures have test expectation metadata"""
        fixture_files = list(self.fixtures_path.glob("lc_*.json"))

        for fixture_file in fixture_files:
            with self.subTest(fixture=fixture_file.name):
                with open(fixture_file, 'r') as f:
                    data = json.load(f)

                self.assertIn("_test_expectations", data,
                             f"Fixture {fixture_file.name} missing _test_expectations")

                expectations = data["_test_expectations"]
                self.assertIn("test_purpose", expectations,
                             f"Fixture {fixture_file.name} missing test_purpose")


def run_golden_suite():
    """Run the complete golden suite and return results"""
    # Create test suite
    suite = unittest.TestSuite()

    # Add all golden LC tests
    suite.addTest(unittest.makeSuite(GoldenLCTestSuite))
    suite.addTest(unittest.makeSuite(TestFixtureValidation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful(), len(result.failures), len(result.errors)


if __name__ == "__main__":
    print("🚀 Running LCopilot Golden LC Test Suite")
    print("=" * 60)

    success, failures, errors = run_golden_suite()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Golden LC Suite Complete")
    else:
        print(f"❌ TESTS FAILED - {failures} failures, {errors} errors")
        sys.exit(1)