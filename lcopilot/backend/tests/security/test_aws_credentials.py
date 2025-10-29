#!/usr/bin/env python3
"""
Security Tests - AWS Credential Handling
Tests that AWS services properly validate and use environment credentials
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
import boto3

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestAWSCredentialSecurity(unittest.TestCase):
    """Test AWS credential handling security"""

    def setUp(self):
        """Set up test environment"""
        # Store original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_textract_requires_aws_credentials(self):
        """Test that TextractOCRFallback requires AWS credentials"""
        from ocr.textract_fallback import TextractFallback, ConfigError

        # Clear AWS credentials
        for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            if key in os.environ:
                del os.environ[key]

        # Should raise ConfigError without credentials
        with self.assertRaises(ConfigError) as context:
            TextractOCRFallback()

        self.assertIn("AWS credentials not found", str(context.exception))

    def test_textract_uses_explicit_credentials(self):
        """Test that TextractOCRFallback uses explicit credentials from environment"""
        from ocr.textract_fallback import TextractFallback

        # Set test credentials
        os.environ['AWS_ACCESS_KEY_ID'] = 'test_access_key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret_key'
        os.environ['AWS_REGION'] = 'us-west-2'

        with patch('boto3.Session') as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client

            # Initialize TextractFallback
            ocr = TextractFallback()

            # Verify Session was called with explicit credentials
            mock_session.assert_called_once_with(
                aws_access_key_id='test_access_key',
                aws_secret_access_key='test_secret_key',
                region_name='us-west-2'
            )

    def test_queue_producer_requires_aws_credentials(self):
        """Test that QueueProducer requires AWS credentials"""
        import importlib
        queue_producer = importlib.import_module('async.queue_producer')
        QueueProducer = queue_producer.QueueProducer
        ConfigError = queue_producer.ConfigError

        # Clear AWS credentials
        for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            if key in os.environ:
                del os.environ[key]

        # Should raise ConfigError without credentials
        with self.assertRaises(ConfigError) as context:
            QueueProducer()

        self.assertIn("AWS credentials not found", str(context.exception))

    def test_queue_producer_uses_explicit_credentials(self):
        """Test that QueueProducer uses explicit credentials from environment"""
        import importlib
        queue_producer = importlib.import_module('async.queue_producer')
        QueueProducer = queue_producer.QueueProducer

        # Set test credentials
        os.environ['AWS_ACCESS_KEY_ID'] = 'test_access_key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret_key'
        os.environ['AWS_REGION'] = 'eu-west-1'

        # Also need Redis password for QueueProducer
        os.environ['REDIS_PASSWORD'] = 'test_redis_password'

        with patch('boto3.Session') as mock_session:
            with patch('redis.Redis'):
                mock_sqs = MagicMock()
                mock_s3 = MagicMock()
                mock_session.return_value.client.side_effect = [mock_sqs, mock_s3]

                # Mock SQS queue operations
                mock_sqs.get_queue_url.return_value = {'QueueUrl': 'test-queue-url'}

                # Initialize QueueProducer
                producer = QueueProducer()

                # Verify Session was called with explicit credentials
                mock_session.assert_called_with(
                    aws_access_key_id='test_access_key',
                    aws_secret_access_key='test_secret_key',
                    region_name='eu-west-1'
                )

    def test_no_implicit_credential_chain(self):
        """Test that AWS clients don't fall back to implicit credential chain"""
        from ocr.textract_fallback import TextractFallback

        # Set only partial credentials (missing secret key)
        os.environ['AWS_ACCESS_KEY_ID'] = 'test_access_key'
        if 'AWS_SECRET_ACCESS_KEY' in os.environ:
            del os.environ['AWS_SECRET_ACCESS_KEY']

        # Should fail even with partial credentials
        with self.assertRaises(Exception) as context:
            TextractOCRFallback()

        self.assertIn("AWS credentials not found", str(context.exception))

    def test_aws_region_configuration(self):
        """Test that AWS region can be configured via environment"""
        from ocr.textract_fallback import TextractFallback

        # Set credentials with custom region
        os.environ['AWS_ACCESS_KEY_ID'] = 'test_access_key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret_key'
        os.environ['AWS_REGION'] = 'ap-southeast-2'

        with patch('boto3.Session') as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client

            # Initialize with custom region
            ocr = TextractFallback()

            # Verify region was used
            mock_session.assert_called_with(
                aws_access_key_id='test_access_key',
                aws_secret_access_key='test_secret_key',
                region_name='ap-southeast-2'
            )


if __name__ == '__main__':
    unittest.main()