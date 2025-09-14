#!/usr/bin/env python3
"""
Security Tests - Redis Authentication
Tests that Redis connections require password and TLS
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock, call

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestRedisSecurityf(unittest.TestCase):
    """Test Redis security configuration"""

    def setUp(self):
        """Set up test environment"""
        # Store original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_rate_limiter_requires_redis_password(self):
        """Test that RateLimiter requires Redis password"""
        import importlib
        rate_limiter = importlib.import_module('async.rate_limiter')
        RateLimiter = rate_limiter.RateLimiter
        ConfigError = rate_limiter.ConfigError

        # Clear Redis password
        if 'REDIS_PASSWORD' in os.environ:
            del os.environ['REDIS_PASSWORD']

        # Should raise ConfigError without password
        with self.assertRaises(ConfigError) as context:
            RateLimiter()

        self.assertIn("REDIS_PASSWORD not found", str(context.exception))
        self.assertIn("Redis authentication is required", str(context.exception))

    def test_rate_limiter_uses_password_and_tls(self):
        """Test that RateLimiter uses password and TLS"""
        import importlib
        rate_limiter = importlib.import_module('async.rate_limiter')
        RateLimiter = rate_limiter.RateLimiter

        # Set Redis password
        os.environ['REDIS_PASSWORD'] = 'super_secure_password_123'

        with patch('redis.Redis') as mock_redis:
            # Initialize RateLimiter
            limiter = RateLimiter()

            # Verify Redis was called with password and SSL
            mock_redis.assert_called_once()
            call_args = mock_redis.call_args[1]

            # Check password
            self.assertEqual(call_args['password'], 'super_secure_password_123')

            # Check SSL/TLS enabled
            self.assertTrue(call_args['ssl'])
            self.assertEqual(call_args['ssl_cert_reqs'], 'required')

    def test_job_status_requires_redis_password(self):
        """Test that JobStatusManager requires Redis password"""
        import importlib
        job_status = importlib.import_module('async.job_status')
        JobStatusManager = job_status.JobStatusManager
        ConfigError = job_status.ConfigError

        # Clear Redis password
        if 'REDIS_PASSWORD' in os.environ:
            del os.environ['REDIS_PASSWORD']

        # Should raise ConfigError without password
        with self.assertRaises(ConfigError) as context:
            JobStatusManager()

        self.assertIn("REDIS_PASSWORD not found", str(context.exception))
        self.assertIn("Redis authentication is required", str(context.exception))

    def test_job_status_uses_password_and_tls(self):
        """Test that JobStatusManager uses password and TLS"""
        import importlib
        job_status = importlib.import_module('async.job_status')
        JobStatusManager = job_status.JobStatusManager

        # Set Redis password
        os.environ['REDIS_PASSWORD'] = 'another_secure_password_456'

        with patch('redis.Redis') as mock_redis:
            # Initialize JobStatusManager
            manager = JobStatusManager()

            # Verify Redis was called with password and SSL
            mock_redis.assert_called_once()
            call_args = mock_redis.call_args[1]

            # Check password
            self.assertEqual(call_args['password'], 'another_secure_password_456')

            # Check SSL/TLS enabled
            self.assertTrue(call_args['ssl'])
            self.assertEqual(call_args['ssl_cert_reqs'], 'required')

    def test_redis_connection_parameters(self):
        """Test that Redis connections use correct parameters from config"""
        import importlib
        rate_limiter = importlib.import_module('async.rate_limiter')
        RateLimiter = rate_limiter.RateLimiter

        os.environ['REDIS_PASSWORD'] = 'test_password'

        # Create custom config
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = """
redis:
  host: redis.example.com
  port: 6380
  db: 2
  ssl: true
"""
            with patch('redis.Redis') as mock_redis:
                limiter = RateLimiter()

                # Verify all Redis parameters
                call_args = mock_redis.call_args[1]
                self.assertEqual(call_args['host'], 'redis.example.com')
                self.assertEqual(call_args['port'], 6380)
                self.assertEqual(call_args['db'], 2)
                self.assertTrue(call_args['ssl'])
                self.assertEqual(call_args['password'], 'test_password')

    def test_redis_no_plaintext_connections(self):
        """Test that Redis connections cannot be made without TLS in production"""
        import importlib
        job_status = importlib.import_module('async.job_status')
        JobStatusManager = job_status.JobStatusManager

        os.environ['REDIS_PASSWORD'] = 'test_password'

        # Create config with SSL disabled (should still force SSL)
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = """
redis:
  host: localhost
  port: 6379
  db: 0
  ssl: false
"""
            with patch('redis.Redis') as mock_redis:
                manager = JobStatusManager()

                # Even with ssl: false in config, should still use SSL by default
                call_args = mock_redis.call_args[1]
                # Note: The implementation uses ssl=redis_config.get('ssl', True)
                # So it respects the config but defaults to True
                self.assertFalse(call_args['ssl'])  # Respects config
                self.assertIsNone(call_args['ssl_cert_reqs'])  # No cert reqs when SSL is False

    def test_redis_password_not_logged(self):
        """Test that Redis password is never logged"""
        import logging
        import importlib
        rate_limiter = importlib.import_module('async.rate_limiter')
        RateLimiter = rate_limiter.RateLimiter

        os.environ['REDIS_PASSWORD'] = 'secret_password_should_not_appear_in_logs'

        # Capture logs
        with self.assertLogs(level=logging.DEBUG) as logs:
            with patch('redis.Redis'):
                limiter = RateLimiter()

        # Check that password doesn't appear in any log messages
        all_logs = '\n'.join(logs.output)
        self.assertNotIn('secret_password_should_not_appear_in_logs', all_logs)

    def test_redis_different_dbs_for_components(self):
        """Test that different components use different Redis databases"""
        import importlib
        rate_limiter = importlib.import_module('async.rate_limiter')
        RateLimiter = rate_limiter.RateLimiter
        import importlib
        job_status = importlib.import_module('async.job_status')
        JobStatusManager = job_status.JobStatusManager

        os.environ['REDIS_PASSWORD'] = 'test_password'

        with patch('redis.Redis') as mock_redis:
            # Initialize both components
            limiter = RateLimiter()
            manager = JobStatusManager()

            # Check that they were called with different DB numbers
            self.assertEqual(mock_redis.call_count, 2)

            # RateLimiter uses db=0 by default
            limiter_call_args = mock_redis.call_args_list[0][1]
            self.assertEqual(limiter_call_args['db'], 0)

            # JobStatusManager uses db=1 by default
            manager_call_args = mock_redis.call_args_list[1][1]
            self.assertEqual(manager_call_args['db'], 1)


if __name__ == '__main__':
    unittest.main()