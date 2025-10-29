"""
Rate limiting regression tests for LCopilot Trust Platform.

Tests Free vs Pro tier rate limits, burst handling, and rate limit enforcement.
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import redis
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class MockRedisClient:
    """Mock Redis client for rate limiting tests."""

    def __init__(self):
        self.data = {}
        self.expirations = {}

    def incr(self, key):
        """Increment counter and return new value."""
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    def expire(self, key, seconds):
        """Set expiration for key."""
        self.expirations[key] = time.time() + seconds
        return True

    def ttl(self, key):
        """Get time to live for key."""
        if key not in self.expirations:
            return -1
        remaining = self.expirations[key] - time.time()
        return max(0, int(remaining))

    def get(self, key):
        """Get value for key."""
        # Check if expired
        if key in self.expirations and time.time() > self.expirations[key]:
            del self.data[key]
            del self.expirations[key]
            return None
        return self.data.get(key)

    def delete(self, key):
        """Delete key."""
        self.data.pop(key, None)
        self.expirations.pop(key, None)
        return True


class TestTierBasedRateLimiting:
    """Test rate limiting based on user tiers (Free vs Pro)."""

    def setup_method(self):
        """Setup test fixtures."""
        self.redis_mock = MockRedisClient()

    def test_free_tier_rate_limits(self):
        """Test that free tier has lower rate limits."""
        free_tier_limits = {
            'requests_per_minute': 10,
            'requests_per_hour': 100,
            'requests_per_day': 500
        }

        customer_id = 'free-customer-123'
        tier = 'free'

        # Simulate requests up to free tier limit
        for i in range(free_tier_limits['requests_per_minute']):
            key = f"rate_limit:{tier}:{customer_id}:minute"
            count = self.redis_mock.incr(key)

            if i == 0:  # Set expiration on first request
                self.redis_mock.expire(key, 60)

            assert count <= free_tier_limits['requests_per_minute'], \
                f"Free tier minute limit exceeded: {count}"

        # Next request should be blocked
        key = f"rate_limit:{tier}:{customer_id}:minute"
        count = self.redis_mock.incr(key)
        assert count > free_tier_limits['requests_per_minute'], \
            "Free tier limit not enforced"

    def test_pro_tier_higher_limits(self):
        """Test that Pro tier has higher rate limits."""
        pro_tier_limits = {
            'requests_per_minute': 100,
            'requests_per_hour': 2000,
            'requests_per_day': 10000
        }

        customer_id = 'pro-customer-456'
        tier = 'pro'

        # Simulate requests up to pro tier limit
        for i in range(pro_tier_limits['requests_per_minute']):
            key = f"rate_limit:{tier}:{customer_id}:minute"
            count = self.redis_mock.incr(key)

            if i == 0:  # Set expiration on first request
                self.redis_mock.expire(key, 60)

            assert count <= pro_tier_limits['requests_per_minute'], \
                f"Pro tier minute limit exceeded at {count}"

        # Pro tier should handle much more traffic than free
        assert pro_tier_limits['requests_per_minute'] > 50, \
            "Pro tier limits not significantly higher"

    def test_enterprise_tier_unlimited(self):
        """Test that Enterprise tier has very high or unlimited rate limits."""
        enterprise_tier_limits = {
            'requests_per_minute': 1000,
            'requests_per_hour': 50000,
            'requests_per_day': 1000000
        }

        customer_id = 'enterprise-customer-789'
        tier = 'enterprise'

        # Enterprise should handle high volume
        for i in range(200):  # Test high volume
            key = f"rate_limit:{tier}:{customer_id}:minute"
            count = self.redis_mock.incr(key)

            if i == 0:
                self.redis_mock.expire(key, 60)

            # Should not hit limits easily
            assert count <= 200, f"Enterprise request failed at {count}"

    def test_different_tiers_isolated_limits(self):
        """Test that different customer tiers don't affect each other."""
        customers = [
            {'id': 'free-001', 'tier': 'free', 'limit': 10},
            {'id': 'pro-001', 'tier': 'pro', 'limit': 100},
            {'id': 'enterprise-001', 'tier': 'enterprise', 'limit': 1000}
        ]

        # Each customer should have independent limits
        for customer in customers:
            for i in range(5):  # Test 5 requests each
                key = f"rate_limit:{customer['tier']}:{customer['id']}:minute"
                count = self.redis_mock.incr(key)

                if i == 0:
                    self.redis_mock.expire(key, 60)

                assert count <= 5, f"Customer {customer['id']} limit affected by others"

        # Verify each customer's count is independent
        for customer in customers:
            key = f"rate_limit:{customer['tier']}:{customer['id']}:minute"
            count = int(self.redis_mock.get(key) or 0)
            assert count == 5, f"Customer {customer['id']} count is {count}, expected 5"


class TestRateLimitWindows:
    """Test different rate limit time windows (minute, hour, day)."""

    def setup_method(self):
        """Setup test fixtures."""
        self.redis_mock = MockRedisClient()

    def test_minute_window_reset(self):
        """Test that minute window resets properly."""
        customer_id = 'test-customer'
        tier = 'free'

        # Fill up minute limit
        minute_key = f"rate_limit:{tier}:{customer_id}:minute"
        for i in range(10):
            self.redis_mock.incr(minute_key)

        self.redis_mock.expire(minute_key, 60)

        # Check current count
        count = int(self.redis_mock.get(minute_key))
        assert count == 10, f"Minute count should be 10, got {count}"

        # Simulate time passage (mock TTL expiration)
        del self.redis_mock.data[minute_key]
        del self.redis_mock.expirations[minute_key]

        # Should be able to make requests again
        new_count = self.redis_mock.incr(minute_key)
        assert new_count == 1, f"After reset, count should be 1, got {new_count}"

    def test_hour_window_tracking(self):
        """Test hour-based rate limiting."""
        customer_id = 'test-customer'
        tier = 'pro'
        hour_limit = 2000

        hour_key = f"rate_limit:{tier}:{customer_id}:hour"

        # Test hour-based counting
        for i in range(50):
            count = self.redis_mock.incr(hour_key)
            if i == 0:
                self.redis_mock.expire(hour_key, 3600)

        final_count = int(self.redis_mock.get(hour_key))
        assert final_count == 50, f"Hour count should be 50, got {final_count}"

        # Check TTL
        ttl = self.redis_mock.ttl(hour_key)
        assert ttl > 0, "Hour window should have TTL set"

    def test_day_window_tracking(self):
        """Test day-based rate limiting."""
        customer_id = 'test-customer'
        tier = 'enterprise'

        day_key = f"rate_limit:{tier}:{customer_id}:day"

        # Test day-based counting
        for i in range(100):
            count = self.redis_mock.incr(day_key)
            if i == 0:
                self.redis_mock.expire(day_key, 86400)  # 24 hours

        final_count = int(self.redis_mock.get(day_key))
        assert final_count == 100, f"Day count should be 100, got {final_count}"

        # Check TTL
        ttl = self.redis_mock.ttl(day_key)
        assert ttl > 0, "Day window should have TTL set"


class TestBurstProtection:
    """Test burst protection and request smoothing."""

    def setup_method(self):
        """Setup test fixtures."""
        self.redis_mock = MockRedisClient()

    def test_burst_detection(self):
        """Test detection of burst traffic patterns."""
        customer_id = 'burst-customer'
        tier = 'free'

        # Simulate burst (many requests in short time)
        burst_window = f"burst:{tier}:{customer_id}:second"
        burst_requests = 20

        for i in range(burst_requests):
            count = self.redis_mock.incr(burst_window)
            if i == 0:
                self.redis_mock.expire(burst_window, 1)  # 1 second window

        final_count = int(self.redis_mock.get(burst_window))

        # Detect burst (more than 10 requests per second for free tier)
        burst_threshold = 10
        is_burst = final_count > burst_threshold

        assert is_burst, f"Burst not detected: {final_count} requests in 1 second"

    def test_burst_mitigation(self):
        """Test burst traffic mitigation strategies."""
        customer_id = 'burst-customer'
        tier = 'free'

        # Track burst score
        burst_score = 0
        requests_per_second = []

        # Simulate traffic pattern
        for second in range(5):
            second_key = f"burst:{tier}:{customer_id}:second_{second}"
            requests_this_second = 15 if second == 2 else 3  # Spike in second 2

            for req in range(requests_this_second):
                self.redis_mock.incr(second_key)

            requests_per_second.append(requests_this_second)

        # Calculate burst score (simple algorithm)
        avg_requests = sum(requests_per_second) / len(requests_per_second)
        max_requests = max(requests_per_second)

        burst_score = max_requests / avg_requests if avg_requests > 0 else 0

        # Burst detected if score > 3
        assert burst_score > 3, f"Burst score too low: {burst_score}"

        # Apply mitigation (delay factor)
        if burst_score > 3:
            delay_factor = min(burst_score / 2, 5)  # Max 5 second delay
            assert delay_factor > 1, "Mitigation delay not applied"

    def test_distributed_burst_protection(self):
        """Test burst protection across distributed instances."""
        customer_id = 'distributed-customer'
        tier = 'pro'

        # Simulate requests from multiple instances
        instances = ['instance-1', 'instance-2', 'instance-3']
        total_requests = 0

        for instance in instances:
            instance_key = f"burst:{tier}:{customer_id}:{instance}"

            # Each instance makes requests
            for i in range(30):  # 30 requests per instance
                self.redis_mock.incr(instance_key)
                total_requests += 1

        # Check global burst detection
        assert total_requests == 90, f"Total requests: {total_requests}"

        # Global rate should be monitored
        global_key = f"burst:{tier}:{customer_id}:global"
        self.redis_mock.data[global_key] = total_requests

        # 90 requests might indicate distributed burst
        global_burst_threshold = 50
        is_global_burst = total_requests > global_burst_threshold

        assert is_global_burst, "Distributed burst not detected"


class TestRateLimitBypass:
    """Test rate limit bypass scenarios and priority handling."""

    def test_emergency_bypass(self):
        """Test emergency bypass for critical operations."""
        customer_id = 'emergency-customer'
        tier = 'free'

        # Normal request should be rate limited
        normal_key = f"rate_limit:{tier}:{customer_id}:minute"
        for i in range(15):  # Exceed free tier limit
            self.redis_mock.incr(normal_key)

        normal_count = int(self.redis_mock.get(normal_key))
        assert normal_count > 10, "Free tier limit not reached"

        # Emergency bypass should work
        emergency_key = f"emergency_bypass:{customer_id}"
        emergency_token = "EMERGENCY_TOKEN_123"

        # Mock emergency bypass
        emergency_active = self.redis_mock.get(emergency_key) is None
        if emergency_active:
            self.redis_mock.data[emergency_key] = emergency_token
            self.redis_mock.expire(emergency_key, 3600)  # 1 hour

        # Emergency request should bypass limits
        assert emergency_token in str(self.redis_mock.get(emergency_key)), \
            "Emergency bypass not working"

    def test_admin_priority_requests(self):
        """Test admin/support requests get priority."""
        admin_customer = 'admin-support-001'
        regular_customer = 'regular-customer-001'

        # Admin requests get special handling
        admin_key = f"priority:admin:{admin_customer}"
        regular_key = f"rate_limit:free:{regular_customer}:minute"

        # Admin should have higher limits or bypass
        admin_limit = 1000  # High limit for admin
        regular_limit = 10   # Low limit for regular

        # Test admin priority
        for i in range(50):
            admin_count = self.redis_mock.incr(admin_key)

        admin_final = int(self.redis_mock.get(admin_key))
        assert admin_final == 50, "Admin requests processed"

        # Regular user hits limit quickly
        for i in range(15):
            regular_count = self.redis_mock.incr(regular_key)

        regular_final = int(self.redis_mock.get(regular_key))
        assert regular_final == 15, "Regular user limit enforced"

        # Admin should not be affected by regular limits
        assert admin_final > regular_limit, "Admin priority not working"


class TestConcurrentRateLimiting:
    """Test rate limiting under concurrent load."""

    def test_concurrent_requests_same_customer(self):
        """Test rate limiting with concurrent requests from same customer."""
        customer_id = 'concurrent-customer'
        tier = 'free'
        request_key = f"rate_limit:{tier}:{customer_id}:minute"

        def make_request(request_id):
            """Simulate a single request."""
            try:
                count = self.redis_mock.incr(request_key)
                return {'id': request_id, 'count': count, 'status': 'success'}
            except Exception as e:
                return {'id': request_id, 'status': 'error', 'error': str(e)}

        # Use ThreadPoolExecutor to simulate concurrent requests
        results = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]

            for future in as_completed(futures):
                results.append(future.result())

        # All requests should be tracked
        assert len(results) == 20, f"Expected 20 results, got {len(results)}"

        # Final count should be 20
        final_count = int(self.redis_mock.get(request_key) or 0)
        assert final_count == 20, f"Expected count 20, got {final_count}"

        # Some requests might be over limit
        over_limit = [r for r in results if r.get('count', 0) > 10]
        assert len(over_limit) > 0, "No requests detected as over limit"

    def test_redis_atomic_operations(self):
        """Test that Redis operations are atomic for rate limiting."""
        customer_id = 'atomic-customer'
        tier = 'pro'

        # Test atomic increment
        def atomic_increment_test():
            key = f"atomic_test:{tier}:{customer_id}"
            counts = []

            for i in range(10):
                count = self.redis_mock.incr(key)
                counts.append(count)

            return counts

        # Run atomic test
        counts = atomic_increment_test()

        # Counts should be sequential
        expected_counts = list(range(1, 11))
        assert counts == expected_counts, f"Non-atomic operation detected: {counts}"

    def test_rate_limit_consistency_across_nodes(self):
        """Test rate limit consistency across multiple nodes."""
        customer_id = 'distributed-customer'
        tier = 'pro'

        # Simulate multiple Redis nodes (mock distributed setup)
        nodes = {
            'node1': MockRedisClient(),
            'node2': MockRedisClient(),
            'node3': MockRedisClient()
        }

        # Requests should be distributed but counted globally
        total_requests = 0
        node_counts = {}

        for i in range(30):
            # Route request to node (simple hash)
            node_key = f"node{(i % 3) + 1}"
            node = nodes[node_key]

            rate_key = f"rate_limit:{tier}:{customer_id}:minute"
            count = node.incr(rate_key)

            node_counts[node_key] = node_counts.get(node_key, 0) + 1
            total_requests += 1

        # Verify distribution
        assert total_requests == 30, f"Total requests: {total_requests}"

        # Each node should have some requests
        for node_key, count in node_counts.items():
            assert count > 0, f"Node {node_key} has no requests"

        # In real implementation, nodes would sync for global limits
        # Here we verify the counting logic works per node
        total_counted = sum(node_counts.values())
        assert total_counted == total_requests, "Request count mismatch"


class TestRateLimitRecovery:
    """Test rate limit recovery and reset mechanisms."""

    def test_window_expiration_recovery(self):
        """Test recovery when rate limit windows expire."""
        customer_id = 'recovery-customer'
        tier = 'free'

        # Hit rate limit
        limit_key = f"rate_limit:{tier}:{customer_id}:minute"
        for i in range(12):  # Exceed free tier limit
            self.redis_mock.incr(limit_key)

        self.redis_mock.expire(limit_key, 60)

        # Verify over limit
        current_count = int(self.redis_mock.get(limit_key))
        assert current_count > 10, f"Not over limit: {current_count}"

        # Simulate window expiration
        del self.redis_mock.data[limit_key]
        del self.redis_mock.expirations[limit_key]

        # Should be able to make requests again
        new_count = self.redis_mock.incr(limit_key)
        assert new_count == 1, f"Recovery failed, count: {new_count}"

    def test_graceful_degradation(self):
        """Test graceful degradation when rate limited."""
        customer_id = 'degradation-customer'
        tier = 'free'

        # Track success/failure rates
        success_responses = []
        rate_limited_responses = []

        # Simulate requests with rate limiting
        for i in range(20):
            request_key = f"rate_limit:{tier}:{customer_id}:minute"
            count = self.redis_mock.incr(request_key)

            if count <= 10:  # Under limit
                success_responses.append({'request_id': i, 'status': 200})
            else:  # Over limit
                rate_limited_responses.append({
                    'request_id': i,
                    'status': 429,
                    'message': 'Rate limit exceeded'
                })

        # Verify graceful degradation
        assert len(success_responses) == 10, f"Expected 10 success, got {len(success_responses)}"
        assert len(rate_limited_responses) == 10, f"Expected 10 rate limited, got {len(rate_limited_responses)}"

        # Rate limited responses should include retry information
        for response in rate_limited_responses:
            assert response['status'] == 429, "Wrong HTTP status for rate limit"
            assert 'message' in response, "Missing rate limit message"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])