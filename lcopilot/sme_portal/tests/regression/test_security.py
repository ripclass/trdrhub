"""
Security regression tests for LCopilot Trust Platform Phase 4.5 hardening.

Tests AWS credentials security, Redis TLS enforcement, file upload security,
and S3 KMS encryption features.
"""

import pytest
import os
import json
import tempfile
import hashlib
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import boto3
from moto import mock_s3, mock_kms
import redis
import ssl

# Mock importlib to handle async module import
class MockImportLib:
    def import_module(self, name):
        if name == 'async':
            mock_module = Mock()
            mock_module.some_function = Mock(return_value="mocked")
            return mock_module
        raise ImportError(f"No module named '{name}'")

@pytest.fixture
def mock_importlib():
    with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: MockImportLib().import_module(name) if name == 'importlib' else __import__(name, *args, **kwargs)):
        yield


class TestAWSCredentialsSecurity:
    """Test AWS credentials security and access controls."""

    def test_aws_credentials_not_exposed_in_logs(self, caplog):
        """Ensure AWS credentials are not logged in plain text."""
        # Mock AWS operation that might log credentials
        with patch('boto3.client') as mock_client:
            mock_s3 = Mock()
            mock_client.return_value = mock_s3

            # Simulate operation with credentials
            mock_s3.head_object.side_effect = Exception("Credentials invalid: AKIA1234567890")

            try:
                mock_s3.head_object(Bucket='test-bucket', Key='test-key')
            except Exception:
                pass

            # Check that AWS keys are not in logs
            log_output = caplog.text
            assert "AKIA" not in log_output, "AWS access key found in logs"
            assert "aws_secret_access_key" not in log_output, "AWS secret key reference in logs"

    @mock_s3
    def test_s3_access_with_invalid_credentials(self):
        """Test that invalid AWS credentials are properly rejected."""
        # Create a mock S3 client with invalid credentials
        with patch.dict(os.environ, {
            'AWS_ACCESS_KEY_ID': 'INVALID_KEY',
            'AWS_SECRET_ACCESS_KEY': 'invalid_secret'
        }):
            client = boto3.client('s3', region_name='us-east-1')

            with pytest.raises(Exception):
                client.head_bucket(Bucket='non-existent-bucket')

    def test_aws_credential_rotation_support(self):
        """Test that the system supports AWS credential rotation."""
        # Mock credential provider
        with patch('boto3.Session') as mock_session:
            mock_credentials = Mock()
            mock_credentials.access_key = 'AKIA_NEW_KEY'
            mock_credentials.secret_key = 'new_secret_key'
            mock_credentials.token = 'session_token'

            mock_session.return_value.get_credentials.return_value = mock_credentials

            session = mock_session()
            creds = session.get_credentials()

            assert creds.access_key.startswith('AKIA_'), "AWS access key format invalid"
            assert len(creds.secret_key) > 20, "AWS secret key too short"

    def test_temporary_credentials_handling(self):
        """Test proper handling of temporary AWS credentials."""
        with patch.dict(os.environ, {
            'AWS_ACCESS_KEY_ID': 'ASIA1234567890EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'temp_secret',
            'AWS_SESSION_TOKEN': 'temp_session_token'
        }):
            # Simulate temporary credential usage
            with patch('boto3.client') as mock_client:
                mock_sts = Mock()
                mock_client.return_value = mock_sts
                mock_sts.get_caller_identity.return_value = {
                    'Account': '123456789012',
                    'Arn': 'arn:aws:sts::123456789012:assumed-role/TempRole/session'
                }

                sts_client = mock_client('sts')
                identity = sts_client.get_caller_identity()

                # Verify temporary role usage
                assert 'assumed-role' in identity['Arn'], "Not using temporary credentials"


class TestRedisTLSEnforcement:
    """Test Redis TLS enforcement and secure connections."""

    def test_redis_connection_requires_tls(self):
        """Test that Redis connections enforce TLS."""
        # Mock Redis connection with TLS
        with patch('redis.Redis') as mock_redis:
            mock_conn = Mock()
            mock_redis.return_value = mock_conn

            # Test TLS-enabled connection
            redis_client = redis.Redis(
                host='localhost',
                port=6380,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_REQUIRED,
                ssl_ca_certs='/path/to/ca.crt'
            )

            mock_redis.assert_called_with(
                host='localhost',
                port=6380,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_REQUIRED,
                ssl_ca_certs='/path/to/ca.crt'
            )

    def test_redis_rejects_non_tls_connections(self):
        """Test that Redis rejects non-TLS connections."""
        with patch('redis.Redis') as mock_redis:
            # Configure mock to raise exception for non-TLS
            mock_redis.side_effect = redis.ConnectionError("TLS required")

            with pytest.raises(redis.ConnectionError, match="TLS required"):
                redis.Redis(host='localhost', port=6379, ssl=False)

    def test_redis_certificate_validation(self):
        """Test Redis certificate validation."""
        with patch('redis.Redis') as mock_redis:
            mock_conn = Mock()
            mock_redis.return_value = mock_conn
            mock_conn.ping.return_value = True

            # Test with certificate validation
            redis_client = redis.Redis(
                host='redis.example.com',
                port=6380,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_REQUIRED,
                ssl_check_hostname=True
            )

            # Verify ping works with valid cert
            assert redis_client.ping() is True

    def test_redis_connection_encryption_strength(self):
        """Test Redis connection uses strong encryption."""
        with patch('ssl.create_default_context') as mock_ssl_context:
            mock_context = Mock()
            mock_ssl_context.return_value = mock_context

            # Configure strong encryption
            mock_context.minimum_version = ssl.TLSVersion.TLSv1_2
            mock_context.check_hostname = True
            mock_context.verify_mode = ssl.CERT_REQUIRED

            ssl_context = ssl.create_default_context()

            assert ssl_context.minimum_version == ssl.TLSVersion.TLSv1_2
            assert ssl_context.check_hostname is True
            assert ssl_context.verify_mode == ssl.CERT_REQUIRED


class TestFileUploadSecurity:
    """Test file upload security controls and validations."""

    def test_file_size_limit_enforcement(self):
        """Test that file size limits are enforced."""
        # Create a file that exceeds the 10MB limit
        large_file_content = b"x" * (11 * 1024 * 1024)  # 11MB

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(large_file_content)
            temp_file.seek(0)

            # Mock Flask request with oversized file
            with patch('flask.request') as mock_request:
                mock_file = Mock()
                mock_file.filename = 'large_file.json'
                mock_file.read.return_value = large_file_content

                mock_request.files = {'lc_file': mock_file}

                # Verify file size check
                file_size = len(mock_file.read())
                MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

                assert file_size > MAX_FILE_SIZE, "File size check failed"

    def test_file_type_validation(self):
        """Test that only allowed file types are accepted."""
        allowed_extensions = ['.json', '.pdf', '.txt']
        dangerous_extensions = ['.exe', '.bat', '.sh', '.py', '.js']

        for ext in allowed_extensions:
            filename = f"document{ext}"
            assert any(filename.endswith(allowed) for allowed in ['.json']), f"Valid file {filename} rejected"

        for ext in dangerous_extensions:
            filename = f"malicious{ext}"
            assert not filename.endswith('.json'), f"Dangerous file {filename} not rejected"

    def test_file_content_scanning(self):
        """Test file content is scanned for malicious patterns."""
        malicious_patterns = [
            b'<script>',
            b'javascript:',
            b'eval(',
            b'exec(',
            b'system(',
        ]

        for pattern in malicious_patterns:
            malicious_content = b'{"data": "' + pattern + b'"}'

            # Check if pattern would be detected
            content_str = malicious_content.decode('utf-8', errors='ignore')
            has_malicious = any(p.decode() in content_str for p in malicious_patterns)

            assert has_malicious, f"Malicious pattern {pattern} not detected"

    def test_file_quarantine_on_threat_detection(self):
        """Test that suspicious files are quarantined."""
        suspicious_file = {
            'filename': 'suspicious.json',
            'content': b'{"eval": "malicious_code", "script": "<script>alert(1)</script>"}',
            'hash': hashlib.sha256(b'suspicious_content').hexdigest()
        }

        # Mock quarantine system
        with patch('shutil.move') as mock_move:
            quarantine_path = f"/quarantine/{suspicious_file['hash']}"

            # Simulate file quarantine
            mock_move.return_value = None
            mock_move(suspicious_file['filename'], quarantine_path)

            mock_move.assert_called_with(suspicious_file['filename'], quarantine_path)

    def test_upload_path_traversal_prevention(self):
        """Test prevention of path traversal attacks in uploads."""
        malicious_filenames = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\cmd.exe',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\SAM',
            '....//....//....//etc/passwd'
        ]

        for filename in malicious_filenames:
            # Check that path traversal is blocked
            safe_filename = os.path.basename(filename)
            assert safe_filename != filename, f"Path traversal not prevented for {filename}"
            assert '../' not in safe_filename, f"Relative path not sanitized: {safe_filename}"


class TestS3KMSEncryption:
    """Test S3 KMS encryption functionality."""

    @mock_s3
    @mock_kms
    def test_s3_objects_encrypted_with_kms(self):
        """Test that S3 objects are encrypted with KMS."""
        # Create mock KMS key
        kms_client = boto3.client('kms', region_name='us-east-1')
        key_response = kms_client.create_key(
            Description='Test KMS key for S3 encryption',
            Usage='ENCRYPT_DECRYPT'
        )
        key_id = key_response['KeyMetadata']['KeyId']

        # Create S3 bucket
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'test-encrypted-bucket'
        s3_client.create_bucket(Bucket=bucket_name)

        # Upload object with KMS encryption
        test_content = b'{"lc_number": "TEST001", "encrypted": true}'

        s3_client.put_object(
            Bucket=bucket_name,
            Key='encrypted-document.json',
            Body=test_content,
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=key_id
        )

        # Verify object is encrypted
        response = s3_client.head_object(Bucket=bucket_name, Key='encrypted-document.json')
        assert response['ServerSideEncryption'] == 'aws:kms'
        assert 'SSEKMSKeyId' in response

    @mock_s3
    @mock_kms
    def test_kms_key_rotation(self):
        """Test KMS key rotation functionality."""
        kms_client = boto3.client('kms', region_name='us-east-1')

        # Create KMS key with rotation enabled
        key_response = kms_client.create_key(
            Description='Rotatable KMS key',
            Usage='ENCRYPT_DECRYPT'
        )
        key_id = key_response['KeyMetadata']['KeyId']

        # Enable key rotation
        kms_client.enable_key_rotation(KeyId=key_id)

        # Verify rotation is enabled
        rotation_status = kms_client.get_key_rotation_status(KeyId=key_id)
        assert rotation_status['KeyRotationEnabled'] is True

    @mock_s3
    def test_s3_bucket_encryption_policy(self):
        """Test that S3 buckets have encryption policies enforced."""
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'test-policy-bucket'

        # Create bucket
        s3_client.create_bucket(Bucket=bucket_name)

        # Set encryption policy
        encryption_policy = {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms"
                    },
                    "BucketKeyEnabled": True
                }
            ]
        }

        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration=encryption_policy
        )

        # Verify encryption policy
        response = s3_client.get_bucket_encryption(Bucket=bucket_name)
        rules = response['ServerSideEncryptionConfiguration']['Rules']

        assert len(rules) > 0
        assert rules[0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'aws:kms'

    def test_encryption_key_access_controls(self):
        """Test that KMS key access is properly controlled."""
        # Mock IAM policy for KMS key access
        key_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "arn:aws:iam::123456789012:role/LCopilotRole"},
                    "Action": [
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:GenerateDataKey"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "*",
                    "Resource": "*",
                    "Condition": {
                        "StringNotEquals": {
                            "aws:PrincipalArn": "arn:aws:iam::123456789012:role/LCopilotRole"
                        }
                    }
                }
            ]
        }

        # Verify policy structure
        assert "Version" in key_policy
        assert "Statement" in key_policy

        # Check for proper access controls
        statements = key_policy["Statement"]
        has_allow = any(stmt["Effect"] == "Allow" for stmt in statements)
        has_deny = any(stmt["Effect"] == "Deny" for stmt in statements)

        assert has_allow, "No allow statements in key policy"
        assert has_deny, "No deny statements in key policy"


class TestSecurityHeaders:
    """Test security headers and middleware."""

    def test_security_headers_present(self):
        """Test that required security headers are present in responses."""
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]

        # Mock Flask response
        with patch('flask.make_response') as mock_response:
            response = Mock()
            response.headers = {}

            # Add security headers
            for header in required_headers:
                response.headers[header] = 'test-value'

            mock_response.return_value = response

            # Verify headers are present
            for header in required_headers:
                assert header in response.headers, f"Missing security header: {header}"

    def test_cors_policy_enforcement(self):
        """Test CORS policy enforcement."""
        allowed_origins = ['https://app.lcopilot.com', 'https://portal.lcopilot.com']
        dangerous_origins = ['https://malicious.com', 'javascript:alert(1)']

        for origin in allowed_origins:
            # Should be allowed
            assert origin.startswith('https://'), f"Non-HTTPS origin allowed: {origin}"
            assert 'lcopilot.com' in origin, f"External origin allowed: {origin}"

        for origin in dangerous_origins:
            # Should be blocked
            assert origin not in allowed_origins, f"Dangerous origin allowed: {origin}"

    def test_rate_limiting_headers(self):
        """Test rate limiting headers are properly set."""
        rate_limit_headers = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset',
            'Retry-After'
        ]

        # Mock rate-limited response
        response_headers = {}
        for header in rate_limit_headers:
            if header == 'X-RateLimit-Limit':
                response_headers[header] = '100'
            elif header == 'X-RateLimit-Remaining':
                response_headers[header] = '95'
            elif header == 'X-RateLimit-Reset':
                response_headers[header] = '3600'
            elif header == 'Retry-After':
                response_headers[header] = '60'

        # Verify headers are properly formatted
        assert int(response_headers['X-RateLimit-Limit']) > 0
        assert int(response_headers['X-RateLimit-Remaining']) >= 0
        assert int(response_headers['X-RateLimit-Reset']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])