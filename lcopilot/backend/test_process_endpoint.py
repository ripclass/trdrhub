#!/usr/bin/env python3
"""
Simple test script for the /process-document endpoint.
This script demonstrates how to call the endpoint with a sample PDF.
"""

import requests
import os
import sys
from pathlib import Path

def test_process_document_endpoint():
    """Test the process document endpoint with a sample PDF."""

    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/documents/process-document"

    # Test file
    test_file = Path("../../sample.pdf")
    if not test_file.exists():
        print("❌ Sample PDF not found. Please run the docai_smoketest.py first to create it.")
        return False

    print(f"🧪 Testing endpoint: {endpoint}")
    print(f"📄 Using test file: {test_file}")

    # Prepare the file for upload
    try:
        with open(test_file, 'rb') as f:
            files = {
                'files': ('sample_lc.pdf', f, 'application/pdf')
            }

            # Make the request
            print("📤 Sending request...")
            response = requests.post(endpoint, files=files)

            print(f"📥 Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Response data:")
                print(f"   Session ID: {data['session_id']}")
                print(f"   Processor ID: {data['processor_id']}")
                print(f"   Documents processed: {len(data['processed_documents'])}")

                if data['processed_documents']:
                    doc = data['processed_documents'][0]
                    print(f"   Document type: {doc['document_type']}")
                    print(f"   File size: {doc['file_size']} bytes")
                    print(f"   OCR confidence: {doc['ocr_confidence']:.3f}")
                    print(f"   Text preview: {doc['extracted_text_preview'][:100]}...")
                    print(f"   Fields found: {len(doc['extracted_fields'])}")

                return True
            else:
                print(f"❌ Request failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text}")
                return False

    except FileNotFoundError:
        print("❌ Test file not found")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    print("🚀 LCopilot Document Processing Endpoint Test")
    print("=" * 50)

    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("⚠️  API server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Start it with:")
        print("   cd apps/api && python3 main.py")
        return

    # Run the test
    success = test_process_document_endpoint()

    if success:
        print("\n🎉 Test completed successfully!")
        print("\nNext steps:")
        print("1. Try uploading multiple files (LC, Invoice, BL)")
        print("2. Check the database for stored results")
        print("3. Test with different file formats (JPEG, PNG)")
    else:
        print("\n💥 Test failed. Check the server logs for details.")

if __name__ == "__main__":
    main()