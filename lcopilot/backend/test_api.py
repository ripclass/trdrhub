"""
Simple test script for LCopilot Mock Backend
Run this to verify the API endpoints work correctly
"""
import requests
import json
import time
import io

API_BASE = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_bank_profiles():
    """Test bank profiles endpoint"""
    print("🏦 Testing bank profiles...")
    response = requests.get(f"{API_BASE}/api/profiles/banks")
    print(f"Status: {response.status_code}")
    banks = response.json()
    print(f"Found {len(banks)} banks:")
    for bank in banks:
        print(f"  - {bank['name']} ({bank['code']}) - {bank['validation_rules']} rules")
    print()
    return banks[0]['code'] if banks else None

def test_current_user():
    """Test current user endpoint"""
    print("👤 Testing current user...")
    response = requests.get(f"{API_BASE}/api/me")
    print(f"Status: {response.status_code}")
    user = response.json()
    print(f"User: {user['email']} ({user['organization']})")
    print(f"Quota: {user['usage']}/{user['quota']}")
    print()

def test_validation_flow(bank_code):
    """Test complete validation flow with enhanced document validation"""
    print("📄 Testing enhanced validation flow...")

    # Create a valid invoice file
    invoice_content = b"Commercial Invoice\nInvoice No: 12345\nSeller: Test Company\nBuyer: Test Client\nTotal Amount: USD 1000"

    # Submit validation with document tags
    print("  1. Submitting validation with document tags...")
    files = [
        ('files', ('test-invoice.pdf', io.BytesIO(invoice_content), 'application/pdf'))
    ]
    document_tags = json.dumps({
        'test-invoice.pdf': 'invoice'
    })
    data = {
        'document_tags': document_tags,
        'user_type': 'exporter',
        'workflow_type': 'export-lc-upload',
        'lc_number': 'LC-TEST-001'
    }
    response = requests.post(f"{API_BASE}/api/validate", files=files, data=data)
    print(f"     Status: {response.status_code}")

    if response.status_code == 200:
        validation_result = response.json()
        job_id = validation_result['job_id']
        print(f"     Job ID: {job_id}")
        print()

        # Poll job status
        print("  2. Polling job status...")
        for i in range(12):  # Poll up to 12 times
            response = requests.get(f"{API_BASE}/api/jobs/{job_id}")
            if response.status_code == 200:
                job = response.json()
                print(f"     Poll {i+1}: {job['status']}/{job['stage']} ({job['progress']}%)")

                if job['status'] == 'completed':
                    print("     ✅ Job completed!")
                    break
            time.sleep(1)
        print()

        # Get results
        print("  3. Getting results...")
        response = requests.get(f"{API_BASE}/api/results/{job_id}")
        if response.status_code == 200:
            results = response.json()
            print(f"     Score: {results['score']}%")
            print(f"     Findings: {len(results['findings'])}")
            print(f"     Evidence URL: {results['evidence_url']}")
            for finding in results['findings']:
                print(f"       - {finding['severity'].upper()}: {finding['description']}")
        else:
            print(f"     Error getting results: {response.status_code}")
        print()

    else:
        print(f"  Validation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        print()

def test_document_validation_features():
    """Test enhanced document validation features"""
    print("🛡️  Testing document validation features...")

    # Test 1: Invalid file type (should be rejected)
    print("  1. Testing invalid file type rejection...")
    invalid_content = b"This is a Word document content"
    files = [('files', ('document.docx', io.BytesIO(invalid_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))]
    data = {
        'document_tags': json.dumps({'document.docx': 'invoice'}),
        'user_type': 'exporter'
    }
    response = requests.post(f"{API_BASE}/api/validate", files=files, data=data)
    print(f"     Status: {response.status_code} {'✅ Rejected' if response.status_code == 400 else '❌ Accepted'}")

    # Test 2: CV uploaded as invoice (should be rejected)
    print("  2. Testing CV rejection when tagged as invoice...")
    cv_content = b"Curriculum Vitae\nJohn Doe\nSoftware Engineer\nExperience: Python development"
    files = [('files', ('cv.pdf', io.BytesIO(cv_content), 'application/pdf'))]
    data = {
        'document_tags': json.dumps({'cv.pdf': 'invoice'}),
        'user_type': 'exporter'
    }
    response = requests.post(f"{API_BASE}/api/validate", files=files, data=data)
    print(f"     Status: {response.status_code} {'✅ Rejected' if response.status_code == 422 else '❌ Accepted'}")
    if response.status_code == 422:
        error_details = response.json()
        print(f"     Error: {error_details['detail']['message']}")

    # Test 3: Valid invoice (should be accepted)
    print("  3. Testing valid invoice acceptance...")
    invoice_content = b"Commercial Invoice\nInvoice No: 12345\nSeller: Export Co\nBuyer: Import Co\nTotal Amount: USD 5000"
    files = [('files', ('invoice.pdf', io.BytesIO(invoice_content), 'application/pdf'))]
    data = {
        'document_tags': json.dumps({'invoice.pdf': 'invoice'}),
        'user_type': 'exporter'
    }
    response = requests.post(f"{API_BASE}/api/validate", files=files, data=data)
    print(f"     Status: {response.status_code} {'✅ Accepted' if response.status_code == 200 else '❌ Rejected'}")

    # Test 4: Bank statement as invoice (should be rejected)
    print("  4. Testing bank statement rejection when tagged as invoice...")
    bank_content = b"Bank Statement\nAccount Number: 123456789\nBalance: USD 10,000\nTransaction History"
    files = [('files', ('bank_statement.pdf', io.BytesIO(bank_content), 'application/pdf'))]
    data = {
        'document_tags': json.dumps({'bank_statement.pdf': 'invoice'}),
        'user_type': 'exporter'
    }
    response = requests.post(f"{API_BASE}/api/validate", files=files, data=data)
    print(f"     Status: {response.status_code} {'✅ Rejected' if response.status_code == 422 else '❌ Accepted'}")

    print()

def test_payment_flow():
    """Test payment flow"""
    print("💳 Testing payment flow...")

    # Create payment session
    response = requests.post(f"{API_BASE}/api/pay/sslcommerz/session", json={
        'amount': 1200,
        'checks': 1
    })
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        session = response.json()
        print(f"Session ID: {session['session_id']}")
        print(f"Redirect URL: {session['redirect_url']}")

        # Test callback
        callback_params = {
            'session_id': session['session_id'],
            'status': 'success',
            'amount': 1200,
            'checks': 1
        }
        response = requests.get(f"{API_BASE}/api/pay/sslcommerz/callback", params=callback_params)
        print(f"Callback Status: {response.status_code}")
        callback_result = response.json()
        print(f"Payment Result: {callback_result['status']}")
        print(f"Transaction ID: {callback_result.get('transaction_id', 'N/A')}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting LCopilot Mock Backend Tests")
    print("=" * 50)

    try:
        test_health()
        bank_code = test_bank_profiles()
        test_current_user()

        # Test enhanced document validation features
        test_document_validation_features()

        if bank_code:
            test_validation_flow(bank_code)

        test_payment_flow()

        print("✅ All tests completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()