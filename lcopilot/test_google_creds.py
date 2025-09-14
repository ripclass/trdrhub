#!/usr/bin/env python3
"""
Google Cloud Credentials Test Script
Tests Google Cloud Storage and Document AI credentials for proper configuration.
"""

import os
import sys
from dotenv import load_dotenv


def load_environment():
    """Load and validate environment variables."""
    # Try to load from .env.production first, then .env
    for env_file in ['.env.production', '.env']:
        if os.path.exists(env_file):
            print(f"📁 Loading environment from {env_file}")
            load_dotenv(env_file)
            break
    else:
        print("⚠️  No .env or .env.production file found, using system environment")
    
    # Check required environment variables
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_DOCUMENTAI_PROCESSOR_ID', 
        'GOOGLE_DOCUMENTAI_LOCATION',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    env_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        env_vars[var] = value
    
    if missing_vars:
        print(f"🔑 Environment Variables: ❌ Missing: {', '.join(missing_vars)}")
        return None, missing_vars
    
    print("🔑 Environment Variables: ✅ All set")
    return env_vars, []


def test_cloud_storage(env_vars):
    """Test Google Cloud Storage credentials."""
    try:
        from google.cloud import storage
        
        # Initialize client - this will use GOOGLE_APPLICATION_CREDENTIALS
        client = storage.Client(project=env_vars['GOOGLE_CLOUD_PROJECT'])
        
        # List buckets to test connectivity
        buckets = list(client.list_buckets())
        bucket_count = len(buckets)
        
        print(f"☁️ Cloud Storage: ✅ Authenticated ({bucket_count} buckets)")
        return True
        
    except ImportError:
        print("☁️ Cloud Storage: ❌ google-cloud-storage library not installed")
        return False
    except Exception as e:
        print(f"☁️ Cloud Storage: ❌ Error - {e}")
        return False


def test_document_ai(env_vars):
    """Test Google Document AI credentials."""
    try:
        from google.cloud import documentai
        
        # Initialize client - this will use GOOGLE_APPLICATION_CREDENTIALS
        client = documentai.DocumentProcessorServiceClient()
        
        # Build processor path
        processor_path = client.processor_path(
            project=env_vars['GOOGLE_CLOUD_PROJECT'],
            location=env_vars['GOOGLE_DOCUMENTAI_LOCATION'],  # Use the location from env
            processor=env_vars['GOOGLE_DOCUMENTAI_PROCESSOR_ID']
        )
        
        # Test by getting processor info
        processor = client.get_processor(name=processor_path)
        processor_id = env_vars['GOOGLE_DOCUMENTAI_PROCESSOR_ID']
        
        print(f"📄 Document AI: ✅ Processor reachable (ID: {processor_id})")
        return True
        
    except ImportError:
        print("📄 Document AI: ❌ google-cloud-documentai library not installed")
        return False
    except Exception as e:
        print(f"📄 Document AI: ❌ Error - {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Starting Google Cloud Credentials Test")
    print("=" * 50)
    
    # Load and validate environment
    env_vars, missing_vars = load_environment()
    
    if missing_vars:
        print(f"❌ Cannot proceed with missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print()
    
    # Run tests
    all_passed = True
    
    # Test Cloud Storage
    storage_ok = test_cloud_storage(env_vars)
    if not storage_ok:
        all_passed = False
    
    # Test Document AI
    doc_ai_ok = test_document_ai(env_vars)
    if not doc_ai_ok:
        all_passed = False
    
    # Final result
    print("=" * 50)
    if all_passed:
        print("🎉 All Google Cloud services are accessible!")
        print("✅ Your Google Cloud configuration is working correctly")
        sys.exit(0)
    else:
        print("❌ Some Google Cloud services failed")
        sys.exit(1)


if __name__ == '__main__':
    main()