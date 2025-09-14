#!/usr/bin/env python3
"""
Comprehensive Bank Profile Demo
Demonstrates different enforcement profiles across all Bangladesh bank categories.
"""

import requests
import json
import sys
from pathlib import Path
import time

def demo_bank_profiles():
    """Demonstrate bank enforcement profiles with realistic scenarios"""

    print("🏦 LCopilot Bank Enforcement Profiles Demo")
    print("=" * 60)
    print("Demonstrating realistic LC validation across all major Bangladesh banks")
    print("")

    # Test LC document - typical SME import scenario
    demo_lc = {
        "lc_number": "DEMO-LC-2024-001",
        "issue_date": "2024-01-15",
        "latest_shipment_date": "2024-02-15",
        "expiry_date": "2024-03-01",
        "expiry_place": "Dhaka, Bangladesh",
        "amount": {
            "value": 125000,
            "currency": "USD"
        },
        "applicant": {
            "name": "Demo Import Company Ltd.",
            "address": "123 Business Avenue, Dhaka-1000",
            "country": "Bangladesh"
        },
        "beneficiary": {
            "name": "Export Solutions Inc.",
            "address": "456 Trade Center, New York, NY 10001",
            "country": "USA"
        },
        "description_of_goods": "Electronics Equipment, HS Code: 8517.12.00",
        "hs_code": "8517.12.00",
        "required_documents": [
            "Commercial Invoice",
            "Bill of Lading",
            "Packing List",
            "Certificate of Origin",
            "Insurance Policy"
        ],
        "insurance_coverage": {
            "percentage": "110%"
        },
        "partial_shipments": "Allowed",
        "transshipment": "Prohibited"
    }

    # Representative banks from each category
    test_banks = [
        # State-owned (Hyper-conservative)
        {
            "code": "SONALI",
            "name": "Sonali Bank Limited",
            "category": "State-Owned",
            "enforcement": "Hyper-Conservative",
            "description": "Largest state bank, extremely strict validation"
        },
        {
            "code": "JANATA",
            "name": "Janata Bank Limited",
            "category": "State-Owned",
            "enforcement": "Hyper-Conservative",
            "description": "Second largest state bank, equally conservative"
        },

        # Private (Moderate)
        {
            "code": "BRAC_BANK",
            "name": "BRAC Bank Limited",
            "category": "Private Commercial",
            "enforcement": "Moderate",
            "description": "SME-friendly with pragmatic approach"
        },
        {
            "code": "DUTCH_BANGLA",
            "name": "Dutch-Bangla Bank Limited",
            "category": "Private Commercial",
            "enforcement": "Moderate",
            "description": "Tech-forward with efficient processing"
        },
        {
            "code": "EASTERN_BANK",
            "name": "Eastern Bank Limited",
            "category": "Private Commercial",
            "enforcement": "Moderate",
            "description": "Leading private bank with standard validation"
        },

        # Islamic (Conservative)
        {
            "code": "ISLAMI_BANK_BD",
            "name": "Islami Bank Bangladesh Limited",
            "category": "Islamic Shariah",
            "enforcement": "Conservative",
            "description": "Largest Islamic bank with Shariah compliance"
        },
        {
            "code": "SHAHJALAL_ISLAMI",
            "name": "Shahjalal Islami Bank Limited",
            "category": "Islamic Shariah",
            "enforcement": "Conservative",
            "description": "Major Islamic bank with conservative validation"
        },

        # Foreign (Very Strict)
        {
            "code": "HSBC",
            "name": "HSBC Bangladesh",
            "category": "Foreign",
            "enforcement": "Very Strict",
            "description": "International standards with premium service"
        },
        {
            "code": "STANDARD_CHARTERED",
            "name": "Standard Chartered Bank",
            "category": "Foreign",
            "enforcement": "Very Strict",
            "description": "UK multinational with comprehensive enforcement"
        }
    ]

    base_url = "http://localhost:5001"

    print(f"📄 Demo LC: {demo_lc['lc_number']} - ${demo_lc['amount']['value']:,} USD")
    print(f"🏭 Importer: {demo_lc['applicant']['name']} (Bangladesh)")
    print(f"🌍 Exporter: {demo_lc['beneficiary']['name']} (USA)")
    print(f"📦 Goods: {demo_lc['description_of_goods']}")
    print("")

    results = []

    for i, bank in enumerate(test_banks, 1):
        print(f"[{i}/{len(test_banks)}] 🏦 Testing {bank['name']}")
        print(f"         Category: {bank['category']} | Enforcement: {bank['enforcement']}")

        try:
            # API call with bank profile
            response = requests.post(
                f"{base_url}/api/validate",
                json={
                    "lc_document": demo_lc,
                    "bank_mode": bank["code"],
                    "tier": "pro",
                    "include_plain_english": True
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                # Extract key metrics
                compliance_score = result.get('compliance_score', 0) * 100
                overall_status = result.get('overall_status', 'unknown')

                bank_info = result.get('bank_profile', {})
                recommendations = result.get('bank_recommendations', [])
                processing = result.get('processing_expectations', {})

                # Status emoji
                status_emoji = {
                    'compliant': '✅',
                    'non_compliant': '❌',
                    'issues_found': '⚠️',
                    'requires_review': '📋'
                }.get(overall_status, '❓')

                print(f"         Result: {status_emoji} {compliance_score:.1f}% - {overall_status.replace('_', ' ').title()}")

                if bank_info:
                    enforcement_desc = bank_info.get('enforcement_config', {}).get('description', 'N/A')
                    print(f"         Profile: {enforcement_desc}")

                if processing:
                    proc_time = processing.get('typical_processing_time', 'N/A')
                    flexibility = processing.get('flexibility_level', 'N/A')
                    print(f"         Processing: {proc_time}, {flexibility} flexibility")

                if recommendations:
                    print(f"         Key Advice: {recommendations[0]}")

                results.append({
                    'bank': bank,
                    'score': compliance_score,
                    'status': overall_status,
                    'enforcement_desc': bank_info.get('enforcement_config', {}).get('description', ''),
                    'processing_time': processing.get('typical_processing_time', 'N/A'),
                    'recommendations': recommendations[:2]
                })

            else:
                print(f"         ❌ API Error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"         ❌ Connection Error: SME Portal not running on {base_url}")
            return False
        except Exception as e:
            print(f"         💥 Error: {str(e)}")

        print("")
        time.sleep(0.5)  # Brief pause for readability

    # Summary analysis
    print("📊 SUMMARY ANALYSIS")
    print("=" * 40)

    # Group by category
    categories = {}
    for result in results:
        cat = result['bank']['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)

    for category, cat_results in categories.items():
        scores = [r['score'] for r in cat_results]
        avg_score = sum(scores) / len(scores) if scores else 0

        print(f"\n🏦 {category} Banks:")
        print(f"   Average Compliance: {avg_score:.1f}%")
        print(f"   Banks Tested: {len(cat_results)}")

        for result in cat_results:
            bank_name = result['bank']['name'].split(' Limited')[0]  # Shorten name
            print(f"   • {bank_name}: {result['score']:.1f}% ({result['status'].replace('_', ' ')})")

    # Insights
    print(f"\n💡 KEY INSIGHTS:")

    all_scores = [r['score'] for r in results]
    if all_scores:
        min_score = min(all_scores)
        max_score = max(all_scores)
        score_range = max_score - min_score

        print(f"   • Score Range: {min_score:.1f}% - {max_score:.1f}% (Δ {score_range:.1f}%)")
        print(f"   • Most Lenient: {max(results, key=lambda x: x['score'])['bank']['name']}")
        print(f"   • Most Strict: {min(results, key=lambda x: x['score'])['bank']['name']}")

        # Category averages
        cat_averages = {}
        for category, cat_results in categories.items():
            cat_scores = [r['score'] for r in cat_results]
            cat_averages[category] = sum(cat_scores) / len(cat_scores) if cat_scores else 0

        print(f"   • Category Ranking (by avg. score):")
        sorted_cats = sorted(cat_averages.items(), key=lambda x: x[1], reverse=True)
        for i, (cat, avg) in enumerate(sorted_cats, 1):
            print(f"     {i}. {cat}: {avg:.1f}%")

    print(f"\n🚀 RECOMMENDATIONS:")
    print(f"   • Test with State-Owned banks first for maximum compliance assurance")
    print(f"   • Use Private banks for balanced business-friendly validation")
    print(f"   • Choose Islamic banks for Shariah-compliant transactions")
    print(f"   • Select Foreign banks for international standard compliance")

    print(f"\n💻 Try it yourself at: {base_url}/validate")
    print("   Select any bank from the dropdown to see bank-specific validation!")

    return True

if __name__ == "__main__":
    success = demo_bank_profiles()
    sys.exit(0 if success else 1)