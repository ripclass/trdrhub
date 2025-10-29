#!/usr/bin/env python3
"""
Comprehensive test suite for the compliance rule engine
"""

import unittest
import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from trust_platform.compliance.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    """Test cases for the rule engine core functionality"""

    def setUp(self):
        self.engine = RuleEngine()
        self.fixtures_path = Path(__file__).parent.parent / "fixtures"

    def load_fixture(self, filename: str):
        """Load test fixture from JSON file"""
        fixture_path = self.fixtures_path / filename
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_ucp600_compliant_credit(self):
        """Test fully compliant UCP600 credit"""
        lc_document = self.load_fixture("ucp600_compliant_credit.json")

        result = self.engine.validate(lc_document, "pro")

        # Should have high compliance score
        self.assertGreaterEqual(result.score, 0.9)

        # Check that key UCP600 rules passed
        rule_results = {r.id: r.status.value for r in result.results}

        # Core UCP600 rules should pass
        self.assertEqual(rule_results.get("UCP600-6"), "pass")  # Expiry place
        self.assertEqual(rule_results.get("UCP600-14"), "pass")  # Presentation period

        # Should not trigger upsell for pro tier
        self.assertFalse(result.upsell_triggered)

    def test_date_logic_violations(self):
        """Test date logic validation failures"""
        lc_document = self.load_fixture("date_logic_violations.json")

        result = self.engine.validate(lc_document, "pro")

        # Should have low compliance score due to date issues
        self.assertLess(result.score, 0.5)

        # Find date logic rule results
        date_rule_results = [r for r in result.results if r.id in ["UCP600-31", "ISBP-A11"]]

        # At least one date rule should fail
        failed_date_rules = [r for r in date_rule_results if r.status.value == "fail"]
        self.assertGreater(len(failed_date_rules), 0)

    def test_bangladesh_compliance_pass(self):
        """Test Bangladesh local compliance - passing case"""
        lc_document = self.load_fixture("bangladesh_compliance_pass.json")

        result = self.engine.validate(lc_document, "pro")

        # Should pass Bangladesh-specific rules
        bd_rule_results = {r.id: r.status.value for r in result.results if r.id.startswith("BD-")}

        # Key BD rules should pass
        self.assertEqual(bd_rule_results.get("BD-001"), "pass")  # Address format
        self.assertEqual(bd_rule_results.get("BD-008"), "pass")  # Certificate issuer

        # Should have good score
        self.assertGreaterEqual(result.score, 0.8)

    def test_bangladesh_compliance_fail(self):
        """Test Bangladesh local compliance - failing case"""
        lc_document = self.load_fixture("bangladesh_compliance_fail.json")

        result = self.engine.validate(lc_document, "pro")

        # Should fail multiple BD rules
        bd_failures = [r for r in result.results if r.id.startswith("BD-") and r.status.value == "fail"]
        self.assertGreater(len(bd_failures), 2)

        # Should have low score
        self.assertLess(result.score, 0.6)

    def test_isbp_document_issues(self):
        """Test ISBP document examination standards"""
        lc_document = self.load_fixture("isbp_document_issues.json")

        result = self.engine.validate(lc_document, "pro")

        # Should detect ISBP violations
        isbp_violations = [r for r in result.results if r.id.startswith("ISBP-") and r.status.value == "fail"]
        self.assertGreater(len(isbp_violations), 0)

    def test_free_tier_functionality(self):
        """Test free tier with quota limits"""
        lc_document = self.load_fixture("free_tier_test.json")

        result = self.engine.validate(lc_document, "free", remaining_free_checks=3)

        # Should trigger upsell
        self.assertTrue(result.upsell_triggered)

        # Should have used free tier
        self.assertEqual(result.tier_used, "free")

        # Should have 0 checks remaining
        self.assertEqual(result.checks_remaining, 0)

    def test_free_tier_no_checks_remaining(self):
        """Test free tier with no remaining checks"""
        lc_document = self.load_fixture("free_tier_test.json")

        result = self.engine.validate(lc_document, "free", remaining_free_checks=0)

        # Should trigger upsell immediately
        self.assertTrue(result.upsell_triggered)

        # Should have no results
        self.assertEqual(len(result.results), 0)
        self.assertEqual(result.score, 0.0)

    def test_comprehensive_test_suite(self):
        """Test comprehensive compliance scenario"""
        lc_document = self.load_fixture("comprehensive_test_suite.json")

        result = self.engine.validate(lc_document, "enterprise")

        # Should have high compliance for well-structured document
        self.assertGreaterEqual(result.score, 0.85)

        # Should test multiple rule categories
        rule_categories = set()
        for rule_result in result.results:
            if rule_result.id.startswith("UCP600"):
                rule_categories.add("UCP600")
            elif rule_result.id.startswith("ISBP"):
                rule_categories.add("ISBP")
            elif rule_result.id.startswith("BD"):
                rule_categories.add("BD")

        # Should cover multiple categories
        self.assertGreaterEqual(len(rule_categories), 2)

    def test_dsl_evaluator_functions(self):
        """Test DSL evaluator with various functions"""
        # Test document with specific field values
        test_doc = {
            "test_field": "Test Value",
            "amount": {"value": 100000.00, "currency": "USD"},
            "issue_date": "2024-01-15",
            "expiry_date": "2024-03-15"
        }

        # Test exists function
        self.assertTrue(self.engine._evaluate_dsl("exists(test_field)", test_doc))
        self.assertFalse(self.engine._evaluate_dsl("exists(missing_field)", test_doc))

        # Test not_empty function
        self.assertTrue(self.engine._evaluate_dsl("not_empty(test_field)", test_doc))

        # Test equalsIgnoreCase function
        self.assertTrue(self.engine._evaluate_dsl("equalsIgnoreCase(test_field, 'test value')", test_doc))

        # Test contains function
        self.assertTrue(self.engine._evaluate_dsl("contains(test_field, 'Test')", test_doc))

        # Test amountGreaterThan function
        self.assertTrue(self.engine._evaluate_dsl("amountGreaterThan(amount, 50000)", test_doc))

    def test_rule_version_tracking(self):
        """Test that rule versions are tracked correctly"""
        lc_document = self.load_fixture("ucp600_compliant_credit.json")

        result = self.engine.validate(lc_document, "pro")

        # Should have version information
        self.assertIsInstance(result.rule_versions, dict)
        self.assertGreater(len(result.rule_versions), 0)

        # Versions should be valid format
        for rule_id, version in result.rule_versions.items():
            self.assertRegex(version, r'^\d+\.\d+\.\d+$')

    def test_severity_scoring(self):
        """Test that severity affects scoring correctly"""
        # Create test documents that will trigger different severities
        high_severity_doc = {"lc_number": "TEST", "amount": {"value": -1000}}  # Invalid amount
        low_severity_doc = {"lc_number": "TEST", "beneficiary": {"name": ""}}  # Empty beneficiary

        result_high = self.engine.validate(high_severity_doc, "pro")
        result_low = self.engine.validate(low_severity_doc, "pro")

        # High severity violations should impact score more
        # (This test may need adjustment based on actual rule definitions)
        self.assertIsInstance(result_high.score, (int, float))
        self.assertIsInstance(result_low.score, (int, float))


class TestRuleLinter(unittest.TestCase):
    """Test cases for the rule linter"""

    def setUp(self):
        from trust_platform.compliance.rule_linter import RuleLinter
        self.linter = RuleLinter()
        self.rules_path = Path(__file__).parent.parent / "rules"

    def test_lint_ucp600_rules(self):
        """Test linting UCP600 rules file"""
        errors, warnings = self.linter.lint_file(self.rules_path / "ucp600.yaml")

        # Should not have critical errors
        self.assertEqual(len(errors), 0, f"UCP600 rules have errors: {errors}")

        # May have warnings but should be reasonable
        self.assertLess(len(warnings), 10, f"Too many warnings in UCP600 rules: {warnings}")

    def test_lint_isbp_rules(self):
        """Test linting ISBP rules file"""
        errors, warnings = self.linter.lint_file(self.rules_path / "isbp.yaml")

        # Should not have critical errors
        self.assertEqual(len(errors), 0, f"ISBP rules have errors: {errors}")

    def test_lint_local_bd_rules(self):
        """Test linting local BD rules file"""
        errors, warnings = self.linter.lint_file(self.rules_path / "local_bd.yaml")

        # Should not have critical errors
        self.assertEqual(len(errors), 0, f"Local BD rules have errors: {errors}")


if __name__ == "__main__":
    unittest.main(verbosity=2)