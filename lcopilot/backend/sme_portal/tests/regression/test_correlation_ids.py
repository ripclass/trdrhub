"""
Correlation ID regression tests for LCopilot Trust Platform.

Tests request ID consistency, distributed tracing, and correlation across services.
"""

import pytest
import uuid
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import threading
import logging
from contextlib import contextmanager


class MockCorrelationContext:
    """Mock correlation context for testing."""

    def __init__(self):
        self.contexts = {}
        self.current_context = {}

    def set_correlation_id(self, correlation_id):
        """Set correlation ID for current context."""
        self.current_context['correlation_id'] = correlation_id
        return correlation_id

    def get_correlation_id(self):
        """Get correlation ID from current context."""
        return self.current_context.get('correlation_id')

    def set_request_id(self, request_id):
        """Set request ID for current context."""
        self.current_context['request_id'] = request_id
        return request_id

    def get_request_id(self):
        """Get request ID from current context."""
        return self.current_context.get('request_id')

    def add_span(self, service_name, operation_name):
        """Add span to trace."""
        span_id = str(uuid.uuid4())
        span = {
            'span_id': span_id,
            'service': service_name,
            'operation': operation_name,
            'start_time': time.time(),
            'correlation_id': self.get_correlation_id(),
            'request_id': self.get_request_id()
        }

        spans = self.current_context.get('spans', [])
        spans.append(span)
        self.current_context['spans'] = spans

        return span

    def finish_span(self, span_id, status='success', metadata=None):
        """Finish a span."""
        spans = self.current_context.get('spans', [])
        for span in spans:
            if span['span_id'] == span_id:
                span['end_time'] = time.time()
                span['duration'] = span['end_time'] - span['start_time']
                span['status'] = status
                span['metadata'] = metadata or {}
                break

    def get_trace_data(self):
        """Get complete trace data."""
        return {
            'correlation_id': self.get_correlation_id(),
            'request_id': self.get_request_id(),
            'spans': self.current_context.get('spans', []),
            'created_at': self.current_context.get('created_at', time.time())
        }


class TestCorrelationIDGeneration:
    """Test correlation ID generation and propagation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.correlation_context = MockCorrelationContext()

    def test_correlation_id_format(self):
        """Test that correlation IDs follow a consistent format."""
        def generate_correlation_id():
            """Generate a new correlation ID."""
            return f"lcop_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Generate multiple correlation IDs
        correlation_ids = []
        for i in range(5):
            correlation_id = generate_correlation_id()
            correlation_ids.append(correlation_id)
            time.sleep(0.001)  # Ensure different timestamps

        # Verify format consistency
        for correlation_id in correlation_ids:
            assert correlation_id.startswith('lcop_'), f"Correlation ID doesn't start with prefix: {correlation_id}"

            parts = correlation_id.split('_')
            assert len(parts) == 3, f"Correlation ID format invalid: {correlation_id}"

            # Verify timestamp part is numeric
            try:
                int(parts[1])
            except ValueError:
                pytest.fail(f"Timestamp part is not numeric: {parts[1]}")

            # Verify UUID part is valid hex
            assert len(parts[2]) == 8, f"UUID part wrong length: {parts[2]}"
            assert all(c in '0123456789abcdef-' for c in parts[2].lower()), \
                f"UUID part contains invalid characters: {parts[2]}"

        # Verify uniqueness
        assert len(set(correlation_ids)) == len(correlation_ids), "Correlation IDs are not unique"

    def test_request_id_generation(self):
        """Test request ID generation and uniqueness."""
        def generate_request_id():
            """Generate a new request ID."""
            return f"req_{str(uuid.uuid4())}"

        # Generate multiple request IDs
        request_ids = []
        for i in range(10):
            request_id = generate_request_id()
            request_ids.append(request_id)

        # Verify format
        for request_id in request_ids:
            assert request_id.startswith('req_'), f"Request ID doesn't start with prefix: {request_id}"

            uuid_part = request_id[4:]  # Remove 'req_' prefix
            try:
                uuid.UUID(uuid_part)  # Validate UUID format
            except ValueError:
                pytest.fail(f"Invalid UUID in request ID: {request_id}")

        # Verify uniqueness
        assert len(set(request_ids)) == len(request_ids), "Request IDs are not unique"

    def test_correlation_id_inheritance(self):
        """Test that child operations inherit parent correlation ID."""
        # Set up parent operation
        parent_correlation_id = "lcop_1234567890_abcd1234"
        self.correlation_context.set_correlation_id(parent_correlation_id)

        # Simulate child operations
        child_operations = []
        for i in range(3):
            # Child operation should inherit parent's correlation ID
            child_correlation_id = self.correlation_context.get_correlation_id()
            child_request_id = f"req_child_{i}"

            child_operations.append({
                'correlation_id': child_correlation_id,
                'request_id': child_request_id,
                'operation': f'child_operation_{i}'
            })

        # Verify inheritance
        for child in child_operations:
            assert child['correlation_id'] == parent_correlation_id, \
                f"Child operation didn't inherit correlation ID: {child['correlation_id']}"

        # Verify each child has unique request ID
        child_request_ids = [child['request_id'] for child in child_operations]
        assert len(set(child_request_ids)) == len(child_request_ids), "Child request IDs not unique"


class TestRequestTracing:
    """Test request tracing across service boundaries."""

    def setup_method(self):
        """Setup test fixtures."""
        self.correlation_context = MockCorrelationContext()

    def test_trace_span_creation(self):
        """Test creation and management of trace spans."""
        # Initialize trace
        correlation_id = "lcop_test_trace"
        request_id = "req_test_001"

        self.correlation_context.set_correlation_id(correlation_id)
        self.correlation_context.set_request_id(request_id)

        # Create spans for different services
        services = [
            ('api_gateway', 'request_validation'),
            ('compliance_engine', 'lc_validation'),
            ('bank_profiles', 'rule_application'),
            ('evidence_packager', 'package_creation')
        ]

        created_spans = []
        for service, operation in services:
            span = self.correlation_context.add_span(service, operation)
            created_spans.append(span)

            # Simulate work
            time.sleep(0.001)

            # Finish span
            self.correlation_context.finish_span(
                span['span_id'],
                status='success',
                metadata={'processed_items': 1}
            )

        # Verify trace structure
        trace_data = self.correlation_context.get_trace_data()

        assert trace_data['correlation_id'] == correlation_id
        assert trace_data['request_id'] == request_id
        assert len(trace_data['spans']) == 4, f"Expected 4 spans, got {len(trace_data['spans'])}"

        # Verify each span has required fields
        for span in trace_data['spans']:
            required_fields = ['span_id', 'service', 'operation', 'start_time', 'end_time',
                             'duration', 'status', 'correlation_id', 'request_id']
            for field in required_fields:
                assert field in span, f"Span missing field: {field}"

            # Verify correlation/request ID consistency
            assert span['correlation_id'] == correlation_id
            assert span['request_id'] == request_id

        # Verify timing
        for span in trace_data['spans']:
            assert span['end_time'] > span['start_time'], "Span end time before start time"
            assert span['duration'] > 0, "Span duration not positive"

    def test_distributed_trace_propagation(self):
        """Test trace propagation across distributed services."""
        # Mock HTTP headers for trace propagation
        def create_trace_headers(correlation_id, request_id, parent_span_id=None):
            """Create HTTP headers for trace propagation."""
            headers = {
                'X-Correlation-ID': correlation_id,
                'X-Request-ID': request_id,
                'X-Trace-ID': correlation_id
            }
            if parent_span_id:
                headers['X-Parent-Span-ID'] = parent_span_id
            return headers

        def extract_trace_from_headers(headers):
            """Extract trace information from HTTP headers."""
            return {
                'correlation_id': headers.get('X-Correlation-ID'),
                'request_id': headers.get('X-Request-ID'),
                'parent_span_id': headers.get('X-Parent-Span-ID')
            }

        # Simulate service A making request to service B
        original_correlation_id = "lcop_distributed_test"
        original_request_id = "req_distributed_001"

        # Service A creates span
        self.correlation_context.set_correlation_id(original_correlation_id)
        self.correlation_context.set_request_id(original_request_id)

        service_a_span = self.correlation_context.add_span('service_a', 'process_request')

        # Service A prepares request to Service B
        outgoing_headers = create_trace_headers(
            original_correlation_id,
            original_request_id,
            service_a_span['span_id']
        )

        # Service B receives request and extracts trace info
        service_b_trace = extract_trace_from_headers(outgoing_headers)

        # Verify propagation
        assert service_b_trace['correlation_id'] == original_correlation_id
        assert service_b_trace['request_id'] == original_request_id
        assert service_b_trace['parent_span_id'] == service_a_span['span_id']

        # Service B creates its own span with inherited trace info
        service_b_span = {
            'span_id': str(uuid.uuid4()),
            'service': 'service_b',
            'operation': 'handle_request',
            'parent_span_id': service_b_trace['parent_span_id'],
            'correlation_id': service_b_trace['correlation_id'],
            'request_id': service_b_trace['request_id']
        }

        # Verify trace continuity
        assert service_b_span['correlation_id'] == original_correlation_id
        assert service_b_span['request_id'] == original_request_id
        assert service_b_span['parent_span_id'] == service_a_span['span_id']

    def test_trace_sampling(self):
        """Test trace sampling for performance optimization."""
        def should_sample_trace(correlation_id, sampling_rate=0.1):
            """Determine if trace should be sampled based on ID."""
            # Use hash of correlation ID for consistent sampling
            hash_value = hash(correlation_id)
            return (hash_value % 100) < (sampling_rate * 100)

        # Test sampling with different correlation IDs
        test_correlation_ids = [
            "lcop_sample_001",
            "lcop_sample_002",
            "lcop_sample_003",
            "lcop_sample_004",
            "lcop_sample_005"
        ]

        sampling_rate = 0.2  # 20% sampling
        sampled_traces = []

        for correlation_id in test_correlation_ids:
            if should_sample_trace(correlation_id, sampling_rate):
                sampled_traces.append(correlation_id)

        # Verify sampling logic is deterministic
        for correlation_id in test_correlation_ids:
            result1 = should_sample_trace(correlation_id, sampling_rate)
            result2 = should_sample_trace(correlation_id, sampling_rate)
            assert result1 == result2, f"Sampling not deterministic for {correlation_id}"

        # Note: Actual sampling percentage may vary due to hash distribution
        # The test verifies the sampling mechanism works consistently


class TestCorrelationIDConsistency:
    """Test correlation ID consistency across different scenarios."""

    def setup_method(self):
        """Setup test fixtures."""
        self.correlation_context = MockCorrelationContext()

    def test_consistency_across_async_operations(self):
        """Test correlation ID consistency in async operations."""
        import threading

        results = []
        correlation_id = "lcop_async_test_001"

        def async_operation(operation_id, correlation_id):
            """Mock async operation that should maintain correlation ID."""
            # Simulate setting correlation context in thread
            local_context = MockCorrelationContext()
            local_context.set_correlation_id(correlation_id)

            # Perform operation
            span = local_context.add_span('async_service', f'operation_{operation_id}')
            time.sleep(0.001)  # Simulate work
            local_context.finish_span(span['span_id'])

            # Record result
            result = {
                'operation_id': operation_id,
                'correlation_id': local_context.get_correlation_id(),
                'span': span
            }
            results.append(result)

        # Start multiple async operations with same correlation ID
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=async_operation,
                args=(i, correlation_id)
            )
            threads.append(thread)
            thread.start()

        # Wait for all operations to complete
        for thread in threads:
            thread.join()

        # Verify consistency
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

        for result in results:
            assert result['correlation_id'] == correlation_id, \
                f"Correlation ID not consistent: {result['correlation_id']}"
            assert result['span']['correlation_id'] == correlation_id, \
                f"Span correlation ID not consistent: {result['span']['correlation_id']}"

    def test_consistency_across_retries(self):
        """Test correlation ID consistency during retry operations."""
        correlation_id = "lcop_retry_test_001"
        request_id = "req_retry_001"

        self.correlation_context.set_correlation_id(correlation_id)
        self.correlation_context.set_request_id(request_id)

        retry_attempts = []
        max_retries = 3

        def operation_with_retries():
            """Mock operation that fails and retries."""
            for attempt in range(max_retries):
                # Each retry should maintain same correlation ID
                current_correlation_id = self.correlation_context.get_correlation_id()
                current_request_id = self.correlation_context.get_request_id()

                span = self.correlation_context.add_span('retry_service', f'attempt_{attempt}')

                attempt_data = {
                    'attempt': attempt,
                    'correlation_id': current_correlation_id,
                    'request_id': current_request_id,
                    'span_id': span['span_id']
                }

                if attempt < 2:  # Fail first two attempts
                    span['status'] = 'failed'
                    span['error'] = f'Attempt {attempt} failed'
                else:  # Succeed on third attempt
                    span['status'] = 'success'

                self.correlation_context.finish_span(span['span_id'], span['status'])
                retry_attempts.append(attempt_data)

                if span['status'] == 'success':
                    break

        operation_with_retries()

        # Verify consistency across retries
        assert len(retry_attempts) == 3, f"Expected 3 retry attempts, got {len(retry_attempts)}"

        for attempt in retry_attempts:
            assert attempt['correlation_id'] == correlation_id, \
                f"Correlation ID changed during retry: {attempt['correlation_id']}"
            assert attempt['request_id'] == request_id, \
                f"Request ID changed during retry: {attempt['request_id']}"

        # Verify attempt sequence
        for i, attempt in enumerate(retry_attempts):
            assert attempt['attempt'] == i, f"Retry attempt sequence incorrect: {attempt['attempt']}"

    def test_consistency_with_error_handling(self):
        """Test correlation ID consistency during error scenarios."""
        correlation_id = "lcop_error_test_001"
        request_id = "req_error_001"

        self.correlation_context.set_correlation_id(correlation_id)
        self.correlation_context.set_request_id(request_id)

        error_scenarios = [
            {'operation': 'validation', 'should_fail': True, 'error_type': 'ValidationError'},
            {'operation': 'processing', 'should_fail': True, 'error_type': 'ProcessingError'},
            {'operation': 'recovery', 'should_fail': False, 'error_type': None}
        ]

        error_results = []

        for scenario in error_scenarios:
            span = self.correlation_context.add_span('error_service', scenario['operation'])

            try:
                if scenario['should_fail']:
                    raise Exception(f"{scenario['error_type']}: {scenario['operation']} failed")
                else:
                    # Success case
                    pass

                self.correlation_context.finish_span(span['span_id'], 'success')
                status = 'success'
                error = None

            except Exception as e:
                self.correlation_context.finish_span(
                    span['span_id'],
                    'error',
                    {'error': str(e)}
                )
                status = 'error'
                error = str(e)

            error_results.append({
                'operation': scenario['operation'],
                'status': status,
                'error': error,
                'correlation_id': self.correlation_context.get_correlation_id(),
                'request_id': self.correlation_context.get_request_id(),
                'span_id': span['span_id']
            })

        # Verify consistency during error handling
        for result in error_results:
            assert result['correlation_id'] == correlation_id, \
                f"Correlation ID lost during error: {result['correlation_id']}"
            assert result['request_id'] == request_id, \
                f"Request ID lost during error: {result['request_id']}"

        # Verify error and success cases were handled
        error_cases = [r for r in error_results if r['status'] == 'error']
        success_cases = [r for r in error_results if r['status'] == 'success']

        assert len(error_cases) == 2, f"Expected 2 error cases, got {len(error_cases)}"
        assert len(success_cases) == 1, f"Expected 1 success case, got {len(success_cases)}"


class TestTraceAggregation:
    """Test trace aggregation and analysis."""

    def setup_method(self):
        """Setup test fixtures."""
        self.correlation_context = MockCorrelationContext()
        self.trace_store = {}

    def test_trace_aggregation_by_correlation_id(self):
        """Test aggregating spans by correlation ID."""
        correlation_ids = ["lcop_agg_001", "lcop_agg_002"]

        # Create traces for different correlation IDs
        all_traces = {}

        for correlation_id in correlation_ids:
            self.correlation_context.set_correlation_id(correlation_id)
            self.correlation_context.set_request_id(f"req_{correlation_id}")

            # Create multiple spans for this correlation ID
            services = ['api', 'compliance', 'database']
            for service in services:
                span = self.correlation_context.add_span(service, 'operation')
                time.sleep(0.001)
                self.correlation_context.finish_span(span['span_id'])

            # Store trace
            all_traces[correlation_id] = self.correlation_context.get_trace_data()

            # Reset context for next trace
            self.correlation_context.current_context = {}

        # Aggregate traces by correlation ID
        def aggregate_traces_by_correlation_id(traces):
            """Aggregate trace data by correlation ID."""
            aggregated = {}

            for correlation_id, trace_data in traces.items():
                aggregated[correlation_id] = {
                    'correlation_id': correlation_id,
                    'request_id': trace_data['request_id'],
                    'span_count': len(trace_data['spans']),
                    'services': list(set(span['service'] for span in trace_data['spans'])),
                    'total_duration': sum(span['duration'] for span in trace_data['spans']),
                    'status': 'success' if all(span['status'] == 'success' for span in trace_data['spans']) else 'error'
                }

            return aggregated

        aggregated_traces = aggregate_traces_by_correlation_id(all_traces)

        # Verify aggregation
        assert len(aggregated_traces) == 2, f"Expected 2 aggregated traces"

        for correlation_id, aggregated in aggregated_traces.items():
            assert aggregated['correlation_id'] == correlation_id
            assert aggregated['span_count'] == 3, f"Expected 3 spans for {correlation_id}"
            assert len(aggregated['services']) == 3, f"Expected 3 services for {correlation_id}"
            assert aggregated['total_duration'] > 0, f"Total duration should be positive for {correlation_id}"
            assert aggregated['status'] == 'success', f"All spans should be successful for {correlation_id}"

    def test_performance_metrics_from_traces(self):
        """Test extracting performance metrics from trace data."""
        correlation_id = "lcop_perf_test_001"
        self.correlation_context.set_correlation_id(correlation_id)
        self.correlation_context.set_request_id("req_perf_001")

        # Create spans with varying durations
        span_configs = [
            {'service': 'api_gateway', 'operation': 'auth', 'duration': 0.05},
            {'service': 'compliance', 'operation': 'validate', 'duration': 0.2},
            {'service': 'database', 'operation': 'query', 'duration': 0.1},
            {'service': 'evidence', 'operation': 'package', 'duration': 0.15}
        ]

        for config in span_configs:
            span = self.correlation_context.add_span(config['service'], config['operation'])

            # Mock duration by setting times manually
            span['start_time'] = time.time()
            span['end_time'] = span['start_time'] + config['duration']
            span['duration'] = config['duration']

            self.correlation_context.finish_span(span['span_id'])

        trace_data = self.correlation_context.get_trace_data()

        # Extract performance metrics
        def extract_performance_metrics(trace_data):
            """Extract performance metrics from trace data."""
            spans = trace_data['spans']

            metrics = {
                'total_request_time': sum(span['duration'] for span in spans),
                'service_breakdown': {},
                'slowest_operation': None,
                'fastest_operation': None,
                'average_operation_time': 0
            }

            # Service breakdown
            for span in spans:
                service = span['service']
                if service not in metrics['service_breakdown']:
                    metrics['service_breakdown'][service] = {
                        'total_time': 0,
                        'operation_count': 0
                    }

                metrics['service_breakdown'][service]['total_time'] += span['duration']
                metrics['service_breakdown'][service]['operation_count'] += 1

            # Slowest and fastest operations
            sorted_spans = sorted(spans, key=lambda x: x['duration'])
            metrics['fastest_operation'] = {
                'service': sorted_spans[0]['service'],
                'operation': sorted_spans[0]['operation'],
                'duration': sorted_spans[0]['duration']
            }
            metrics['slowest_operation'] = {
                'service': sorted_spans[-1]['service'],
                'operation': sorted_spans[-1]['operation'],
                'duration': sorted_spans[-1]['duration']
            }

            # Average operation time
            metrics['average_operation_time'] = metrics['total_request_time'] / len(spans)

            return metrics

        metrics = extract_performance_metrics(trace_data)

        # Verify metrics
        assert abs(metrics['total_request_time'] - 0.5) < 0.01, f"Total time incorrect: {metrics['total_request_time']}"
        assert len(metrics['service_breakdown']) == 4, f"Expected 4 services in breakdown"

        # Verify slowest operation (compliance with 0.2s)
        assert metrics['slowest_operation']['service'] == 'compliance'
        assert metrics['slowest_operation']['duration'] == 0.2

        # Verify fastest operation (api_gateway with 0.05s)
        assert metrics['fastest_operation']['service'] == 'api_gateway'
        assert metrics['fastest_operation']['duration'] == 0.05

        # Verify average
        expected_average = 0.5 / 4  # Total time / number of spans
        assert abs(metrics['average_operation_time'] - expected_average) < 0.01, \
            f"Average time incorrect: {metrics['average_operation_time']}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])