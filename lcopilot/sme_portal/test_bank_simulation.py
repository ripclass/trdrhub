#!/usr/bin/env python3
"""
Test script for Bank-Mode Simulator integration
"""
import json
import requests
import sys
from pathlib import Path

def test_bank_simulation():
    """Test the bank simulation functionality"""

    # Test LC document
    test_lc = {
        "lc_number": "TEST-LC-001",
        "issue_date": "2024-01-15",
        "latest_shipment_date": "2024-02-15",
        "expiry_date": "2024-03-01",
        "amount": {
            "value": 150000,
            "currency": "USD"
        },
        "applicant": {
            "name": "Test Company Ltd.",
            "address": "123 Test Street, Dhaka-1000",
            "country": "Bangladesh"
        },
        "beneficiary": {
            "name": "Export Solutions Inc.",
            "address": "456 Export Ave, New York, NY",
            "country": "USA"
        },
        "description_of_goods": "Cotton Textiles",
        "hs_code": "5208.11.00",
        "required_documents": [
            "Commercial Invoice",
            "Bill of Lading",
            "Insurance Policy"
        ],
        "insurance_coverage": {
            "percentage": "110%"
        }
    }

    # Test different banks
    banks_to_test = [
        ("sonali_bank", "Sonali Bank (Conservative)"),
        ("dbbl", "DBBL (Efficient)"),
        ("hsbc_bangladesh", "HSBC Bangladesh (Premium)")
    ]

    print("🧪 Testing Bank-Mode Simulator Integration")
    print("=" * 60)

    base_url = "http://localhost:5001"

    for bank_code, bank_name in banks_to_test:
        print(f"\n🏦 Testing {bank_name}")
        print("-" * 40)

        # Test API endpoint
        try:
            response = requests.post(f"{base_url}/api/validate", json={
                "lc_document": test_lc,
                "tier": "pro",
                "bank_mode": bank_code,
                "include_plain_english": True
            }, timeout=10)

            if response.status_code == 200:
                result = response.json()

                print(f"✅ API Response: {response.status_code}")
                print(f"📊 Compliance Score: {result.get('compliance_score', 0)*100:.1f}%")
                print(f"📋 Overall Status: {result.get('overall_status', 'unknown')}")

                # Check for bank simulation data
                if 'bank_simulation' in result:
                    bank_sim = result['bank_simulation']
                    print(f"🏦 Bank Info: {bank_sim.get('bank_info', {}).get('name', 'N/A')}")
                    print(f"⏱️  Processing Time: {bank_sim.get('simulation_metadata', {}).get('simulated_processing_time_ms', 0):.0f}ms")

                    if bank_sim.get('bank_recommendations'):
                        print(f"💡 Recommendations: {len(bank_sim.get('bank_recommendations', []))}")
                        for i, rec in enumerate(bank_sim.get('bank_recommendations', [])[:2], 1):
                            print(f"   {i}. {rec}")
                else:
                    print("⚠️  No bank simulation data found")

            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")

        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Make sure Flask app is running on {base_url}")
            return False
        except Exception as e:
            print(f"❌ Test Error: {str(e)}")
            return False

    print(f"\n🎉 Bank simulation tests completed!")
    print(f"\n💻 You can now test manually at: {base_url}/validate")
    print("   1. Select a bank from the dropdown")
    print("   2. Upload an LC or paste JSON")
    print("   3. See bank-specific validation results")

    return True

if __name__ == "__main__":
    success = test_bank_simulation()
    sys.exit(0 if success else 1)