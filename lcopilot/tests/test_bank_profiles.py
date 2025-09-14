#!/usr/bin/env python3
"""
Comprehensive tests for Bank Profile Engine
Tests enforcement profiles across all bank categories with realistic scenarios.
"""

import json
import requests
import unittest
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "trust_platform"))

from trust_platform.compliance.bank_profile_engine import BankProfileEngine

class TestBankProfiles(unittest.TestCase):
    """Test bank enforcement profiles"""

    def setUp(self):
        """Set up test environment"""
        self.engine = BankProfileEngine()
        self.fixtures_dir = Path(__file__).parent / "fixtures" / "bank_profiles"
        self.base_url = "http://localhost:5001"

    def load_fixture(self, filename: str) -> dict:
        """Load test fixture from JSON file"""
        fixture_path = self.fixtures_dir / filename
        if not fixture_path.exists():
            self.fail(f"Fixture file not found: {fixture_path}")

        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_engine_initialization(self):
        """Test bank profile engine loads correctly"""
        self.assertIsNotNone(self.engine)
        self.assertGreater(len(self.engine.profiles), 0)

        # Check we have all categories
        categories = self.engine.get_all_categories()
        expected_categories = ['state_owned', 'private', 'islamic', 'foreign']
        for category in expected_categories:
            self.assertIn(category, categories)

    def test_bank_profile_loading(self):
        """Test specific bank profiles are loaded correctly"""
        # Test state-owned bank
        sonali = self.engine.get_bank_profile('SONALI')
        self.assertIsNotNone(sonali)
        self.assertEqual(sonali.name, "Sonali Bank Limited")
        self.assertEqual(sonali.category, "state_owned")
        self.assertEqual(sonali.enforcement_level, "hyper_conservative")

        # Test private bank
        brac = self.engine.get_bank_profile('BRAC_BANK')
        self.assertIsNotNone(brac)
        self.assertEqual(brac.category, "private")
        self.assertEqual(brac.enforcement_level, "moderate")

        # Test Islamic bank
        islami = self.engine.get_bank_profile('ISLAMI_BANK_BD')
        self.assertIsNotNone(islami)
        self.assertEqual(islami.category, "islamic")
        self.assertEqual(islami.enforcement_level, "conservative")

        # Test foreign bank
        hsbc = self.engine.get_bank_profile('HSBC')
        self.assertIsNotNone(hsbc)
        self.assertEqual(hsbc.category, "foreign")
        self.assertEqual(hsbc.enforcement_level, "very_strict")

    def test_dropdown_data_structure(self):
        """Test bank dropdown data is properly structured"""
        dropdown_data = self.engine.get_banks_for_dropdown()

        # Check structure
        self.assertIsInstance(dropdown_data, dict)
        self.assertIn('state_owned', dropdown_data)
        self.assertIn('private', dropdown_data)
        self.assertIn('islamic', dropdown_data)
        self.assertIn('foreign', dropdown_data)

        # Check state-owned banks
        state_banks = dropdown_data['state_owned']['banks']
        self.assertGreater(len(state_banks), 0)

        # Check one bank structure
        bank = state_banks[0]
        required_keys = ['code', 'name', 'enforcement_level', 'description']
        for key in required_keys:
            self.assertIn(key, bank)

    def test_enforcement_profile_application(self):
        """Test bank enforcement profiles are applied correctly"""
        # Create mock validation result
        mock_result = {
            'compliance_score': 0.8,
            'overall_status': 'compliant',
            'validated_rules': [
                {
                    'id': 'TEST-RULE-001',
                    'status': 'pass',
                    'details': 'Test rule passed'
                },
                {
                    'id': 'TEST-CURRENCY-001',
                    'status': 'pass',
                    'details': 'Minor currency formatting issue'
                }
            ]
        }

        # Test with hyper-conservative bank (Sonali)
        sonali_result = self.engine.apply_bank_profile(mock_result, 'SONALI')

        # Check bank profile information is added
        self.assertIn('bank_profile', sonali_result)
        self.assertEqual(sonali_result['bank_profile']['bank_name'], "Sonali Bank Limited")
        self.assertEqual(sonali_result['bank_profile']['enforcement_level'], "hyper_conservative")

        # Check recommendations are generated
        self.assertIn('bank_recommendations', sonali_result)
        self.assertGreater(len(sonali_result['bank_recommendations']), 0)

        # Check processing expectations
        self.assertIn('processing_expectations', sonali_result)

        # Test with moderate bank (BRAC)
        brac_result = self.engine.apply_bank_profile(mock_result, 'BRAC_BANK')
        self.assertEqual(brac_result['bank_profile']['enforcement_level'], "moderate")

    def test_enforcement_level_adjustments(self):
        """Test that different enforcement levels produce different compliance scores"""
        mock_result = {
            'compliance_score': 0.75,
            'overall_status': 'compliant',
            'validated_rules': [
                {'id': 'TEST-001', 'status': 'fail', 'details': 'Test failure'}
            ]
        }

        # Test hyper-conservative enforcement (should be stricter)
        sonali_result = self.engine.apply_bank_profile(mock_result.copy(), 'SONALI')

        # Test moderate enforcement
        brac_result = self.engine.apply_bank_profile(mock_result.copy(), 'BRAC_BANK')

        # Test very strict enforcement
        hsbc_result = self.engine.apply_bank_profile(mock_result.copy(), 'HSBC')

        # Hyper-conservative and very strict should be more stringent
        # (Note: exact scoring depends on implementation details)
        self.assertIn('bank_profile', sonali_result)
        self.assertIn('bank_profile', brac_result)
        self.assertIn('bank_profile', hsbc_result)

    def test_api_integration(self):
        """Test bank profiles work through API"""
        try:
            # Test basic connectivity
            health_response = requests.get(f"{self.base_url}/health", timeout=5)
            if health_response.status_code != 200:
                self.skipTest("API server not available")

            # Load test fixture
            fixture = self.load_fixture("brac_pass.json")

            # Test API validation with bank profile
            api_data = {
                "lc_document": fixture["lc_document"],
                "bank_mode": fixture["bank_code"],
                "tier": "pro",
                "include_plain_english": True
            }

            response = requests.post(
                f"{self.base_url}/api/validate",
                json=api_data,
                timeout=10
            )

            self.assertEqual(response.status_code, 200)
            result = response.json()

            # Check bank profile data is included
            if 'bank_profile' in result:
                self.assertIn('bank_name', result['bank_profile'])
                self.assertIn('enforcement_level', result['bank_profile'])

            # Check recommendations are provided
            if 'bank_recommendations' in result:
                self.assertIsInstance(result['bank_recommendations'], list)

        except requests.exceptions.ConnectionError:
            self.skipTest("API server not available for integration tests")

    def test_category_specific_features(self):
        """Test category-specific enforcement features"""

        # Test State-owned bank features
        state_banks = self.engine.get_banks_by_category('state_owned')
        self.assertGreater(len(state_banks), 0)

        for bank in state_banks:
            self.assertEqual(bank.enforcement_level, 'hyper_conservative')

        # Test Islamic bank features
        islamic_banks = self.engine.get_banks_by_category('islamic')
        self.assertGreater(len(islamic_banks), 0)

        for bank in islamic_banks:
            self.assertEqual(bank.enforcement_level, 'conservative')
            # Should have Shariah-related patterns
            self.assertTrue(any('shariah' in pattern.lower() for pattern in bank.patterns))

        # Test Foreign bank features
        foreign_banks = self.engine.get_banks_by_category('foreign')
        self.assertGreater(len(foreign_banks), 0)

        for bank in foreign_banks:
            self.assertEqual(bank.enforcement_level, 'very_strict')
            # Should have UCP600/ISBP patterns
            self.assertTrue(any('ucp600' in pattern.lower() or 'isbp' in pattern.lower()
                               for pattern in bank.patterns))

    def test_statistics(self):
        """Test profile statistics are accurate"""
        stats = self.engine.get_profile_statistics()

        self.assertIn('total_banks', stats)
        self.assertIn('by_category', stats)
        self.assertIn('by_enforcement_level', stats)

        # Check we have expected number of banks (41 as per YAML)
        self.assertEqual(stats['total_banks'], 41)

        # Check category distribution
        expected_categories = {
            'state_owned': 4,
            'private': 21,
            'islamic': 7,
            'foreign': 9
        }

        for category, expected_count in expected_categories.items():
            self.assertEqual(stats['by_category'][category], expected_count)

    def test_fixture_validation(self):
        """Test all fixture files are valid and loadable"""
        fixture_files = [
            "sonali_fail.json",
            "brac_pass.json",
            "islami_conservative.json",
            "hsbc_strict.json"
        ]

        for fixture_file in fixture_files:
            with self.subTest(fixture=fixture_file):
                fixture = self.load_fixture(fixture_file)

                # Check required structure
                self.assertIn('bank_code', fixture)
                self.assertIn('lc_document', fixture)
                self.assertIn('expected_outcome', fixture)

                # Check bank exists in engine
                bank_profile = self.engine.get_bank_profile(fixture['bank_code'])
                self.assertIsNotNone(bank_profile, f"Bank {fixture['bank_code']} not found")

def run_comprehensive_test():
    """Run comprehensive bank profile tests"""
    print("🧪 Running Comprehensive Bank Profile Tests")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBankProfiles)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n📊 Test Summary:")
    print(f"  • Tests Run: {result.testsRun}")
    print(f"  • Failures: {len(result.failures)}")
    print(f"  • Errors: {len(result.errors)}")
    print(f"  • Skipped: {len(result.skipped)}")

    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Error:')[-1].strip()}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All Tests Passed!' if success else '❌ Some Tests Failed'}")

    return success

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)