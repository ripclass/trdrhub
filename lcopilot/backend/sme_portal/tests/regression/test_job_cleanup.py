"""
Job cleanup regression tests for LCopilot Trust Platform.

Tests old job cleanup processes, async job management, and resource cleanup.
"""

import pytest
import time
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import threading
import queue
import os
import shutil


class MockJobStore:
    """Mock job store for testing cleanup operations."""

    def __init__(self):
        self.jobs = {}
        self.completed_jobs = {}
        self.failed_jobs = {}

    def add_job(self, job_id, job_data, status='pending'):
        """Add a job to the store."""
        self.jobs[job_id] = {
            'id': job_id,
            'status': status,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'data': job_data
        }

    def complete_job(self, job_id, result=None):
        """Mark job as completed."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job['status'] = 'completed'
            job['completed_at'] = datetime.now()
            job['result'] = result
            self.completed_jobs[job_id] = job
            return True
        return False

    def fail_job(self, job_id, error=None):
        """Mark job as failed."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job['status'] = 'failed'
            job['failed_at'] = datetime.now()
            job['error'] = error
            self.failed_jobs[job_id] = job
            return True
        return False

    def get_jobs_older_than(self, days):
        """Get jobs older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_jobs = []

        for job in self.jobs.values():
            if job['created_at'] < cutoff_date:
                old_jobs.append(job)

        return old_jobs

    def delete_job(self, job_id):
        """Delete a job from the store."""
        deleted = False
        if job_id in self.jobs:
            del self.jobs[job_id]
            deleted = True
        if job_id in self.completed_jobs:
            del self.completed_jobs[job_id]
            deleted = True
        if job_id in self.failed_jobs:
            del self.failed_jobs[job_id]
            deleted = True
        return deleted

    def get_job_count_by_status(self, status):
        """Get count of jobs by status."""
        return len([job for job in self.jobs.values() if job['status'] == status])


class TestJobCleanupBasics:
    """Test basic job cleanup functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.job_store = MockJobStore()

    def test_cleanup_old_completed_jobs(self):
        """Test cleanup of old completed jobs."""
        # Create some old completed jobs
        old_date = datetime.now() - timedelta(days=8)  # 8 days old

        for i in range(5):
            job_id = f"old_job_{i}"
            self.job_store.add_job(job_id, {'type': 'lc_validation'}, 'completed')
            # Manually set old date
            self.job_store.jobs[job_id]['created_at'] = old_date
            self.job_store.jobs[job_id]['completed_at'] = old_date

        # Add some recent jobs
        for i in range(3):
            job_id = f"recent_job_{i}"
            self.job_store.add_job(job_id, {'type': 'lc_validation'}, 'completed')

        # Test cleanup (remove jobs older than 7 days)
        old_jobs = self.job_store.get_jobs_older_than(7)
        assert len(old_jobs) == 5, f"Expected 5 old jobs, found {len(old_jobs)}"

        # Cleanup old jobs
        cleaned_count = 0
        for job in old_jobs:
            if self.job_store.delete_job(job['id']):
                cleaned_count += 1

        assert cleaned_count == 5, f"Expected to clean 5 jobs, cleaned {cleaned_count}"

        # Verify recent jobs remain
        remaining_jobs = len(self.job_store.jobs)
        assert remaining_jobs == 3, f"Expected 3 remaining jobs, found {remaining_jobs}"

    def test_cleanup_failed_jobs_retention(self):
        """Test that failed jobs are retained longer than completed jobs."""
        # Create old failed jobs
        old_date = datetime.now() - timedelta(days=15)  # 15 days old

        for i in range(3):
            job_id = f"failed_job_{i}"
            self.job_store.add_job(job_id, {'type': 'lc_validation'}, 'failed')
            self.job_store.jobs[job_id]['created_at'] = old_date
            self.job_store.fail_job(job_id, "Processing error")

        # Create old completed jobs
        for i in range(3):
            job_id = f"completed_job_{i}"
            self.job_store.add_job(job_id, {'type': 'lc_validation'}, 'completed')
            self.job_store.jobs[job_id]['created_at'] = old_date
            self.job_store.complete_job(job_id, "Success")

        # Cleanup policy: completed jobs > 7 days, failed jobs > 30 days
        jobs_7_days = self.job_store.get_jobs_older_than(7)
        jobs_30_days = self.job_store.get_jobs_older_than(30)

        # All jobs are 15 days old, so all appear in 7-day filter
        assert len(jobs_7_days) == 6, f"Expected 6 jobs older than 7 days, found {len(jobs_7_days)}"

        # None should appear in 30-day filter (jobs are only 15 days old)
        assert len(jobs_30_days) == 0, f"Expected 0 jobs older than 30 days, found {len(jobs_30_days)}"

        # Cleanup completed jobs (7+ days old)
        completed_cleaned = 0
        for job in jobs_7_days:
            if job['status'] == 'completed':
                self.job_store.delete_job(job['id'])
                completed_cleaned += 1

        assert completed_cleaned == 3, f"Expected to clean 3 completed jobs, cleaned {completed_cleaned}"

        # Failed jobs should remain
        remaining_failed = self.job_store.get_job_count_by_status('failed')
        assert remaining_failed == 3, f"Expected 3 failed jobs to remain, found {remaining_failed}"

    def test_cleanup_preserves_running_jobs(self):
        """Test that running/pending jobs are never cleaned up."""
        # Create old jobs in various states
        old_date = datetime.now() - timedelta(days=10)

        job_states = ['pending', 'running', 'completed', 'failed']

        for state in job_states:
            for i in range(2):
                job_id = f"{state}_job_{i}"
                self.job_store.add_job(job_id, {'type': 'lc_validation'}, state)
                self.job_store.jobs[job_id]['created_at'] = old_date

        # Get old jobs
        old_jobs = self.job_store.get_jobs_older_than(7)
        assert len(old_jobs) == 8, f"Expected 8 old jobs, found {len(old_jobs)}"

        # Cleanup should only remove completed and failed jobs
        preserved_states = ['pending', 'running']
        cleaned_count = 0

        for job in old_jobs:
            if job['status'] not in preserved_states:
                self.job_store.delete_job(job['id'])
                cleaned_count += 1

        assert cleaned_count == 4, f"Expected to clean 4 jobs, cleaned {cleaned_count}"

        # Verify pending and running jobs remain
        remaining_pending = self.job_store.get_job_count_by_status('pending')
        remaining_running = self.job_store.get_job_count_by_status('running')

        assert remaining_pending == 2, f"Expected 2 pending jobs to remain"
        assert remaining_running == 2, f"Expected 2 running jobs to remain"


class TestAsyncJobCleanup:
    """Test cleanup of async processing jobs."""

    def setup_method(self):
        """Setup test fixtures."""
        self.job_store = MockJobStore()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_cleanup_async_job_artifacts(self):
        """Test cleanup of async job artifacts (files, temp data)."""
        # Create async jobs with file artifacts
        for i in range(3):
            job_id = f"async_job_{i}"
            artifact_path = Path(self.temp_dir) / f"artifact_{i}.json"

            # Create artifact file
            artifact_data = {'job_id': job_id, 'result': f'processed_{i}'}
            artifact_path.write_text(json.dumps(artifact_data))

            # Add job to store
            self.job_store.add_job(job_id, {
                'type': 'async_lc_validation',
                'artifact_path': str(artifact_path)
            }, 'completed')

            # Make job old
            old_date = datetime.now() - timedelta(days=8)
            self.job_store.jobs[job_id]['created_at'] = old_date

        # Verify artifacts exist
        artifact_files = list(Path(self.temp_dir).glob("artifact_*.json"))
        assert len(artifact_files) == 3, f"Expected 3 artifact files, found {len(artifact_files)}"

        # Cleanup old async jobs
        old_jobs = self.job_store.get_jobs_older_than(7)
        cleaned_artifacts = 0

        for job in old_jobs:
            artifact_path = job['data'].get('artifact_path')
            if artifact_path and os.path.exists(artifact_path):
                os.remove(artifact_path)
                cleaned_artifacts += 1
            self.job_store.delete_job(job['id'])

        assert cleaned_artifacts == 3, f"Expected to clean 3 artifacts, cleaned {cleaned_artifacts}"

        # Verify artifacts are gone
        remaining_artifacts = list(Path(self.temp_dir).glob("artifact_*.json"))
        assert len(remaining_artifacts) == 0, f"Expected 0 remaining artifacts, found {len(remaining_artifacts)}"

    def test_cleanup_async_queue_messages(self):
        """Test cleanup of stale async queue messages."""
        # Mock message queue
        message_queue = queue.Queue()

        # Add old messages
        old_timestamp = time.time() - (8 * 24 * 3600)  # 8 days ago

        for i in range(5):
            message = {
                'job_id': f'queue_job_{i}',
                'timestamp': old_timestamp,
                'payload': {'type': 'lc_validation'}
            }
            message_queue.put(message)

        # Add recent messages
        recent_timestamp = time.time() - 3600  # 1 hour ago

        for i in range(3):
            message = {
                'job_id': f'recent_job_{i}',
                'timestamp': recent_timestamp,
                'payload': {'type': 'lc_validation'}
            }
            message_queue.put(message)

        # Process queue and cleanup old messages
        processed_messages = []
        cleaned_messages = []

        while not message_queue.empty():
            message = message_queue.get()

            # Check if message is old (7 days)
            message_age_seconds = time.time() - message['timestamp']
            message_age_days = message_age_seconds / (24 * 3600)

            if message_age_days > 7:
                cleaned_messages.append(message)
            else:
                processed_messages.append(message)

        assert len(cleaned_messages) == 5, f"Expected 5 old messages, found {len(cleaned_messages)}"
        assert len(processed_messages) == 3, f"Expected 3 recent messages, found {len(processed_messages)}"

    def test_cleanup_async_job_dependencies(self):
        """Test cleanup of job dependencies and related resources."""
        # Create parent job with dependencies
        parent_job_id = "parent_job_001"
        self.job_store.add_job(parent_job_id, {
            'type': 'batch_lc_validation',
            'dependencies': ['dep1', 'dep2', 'dep3']
        }, 'completed')

        # Create dependent jobs
        dependent_jobs = []
        for i, dep_id in enumerate(['dep1', 'dep2', 'dep3']):
            self.job_store.add_job(dep_id, {
                'type': 'lc_validation',
                'parent_job': parent_job_id
            }, 'completed')
            dependent_jobs.append(dep_id)

        # Make all jobs old
        old_date = datetime.now() - timedelta(days=10)
        for job_id in [parent_job_id] + dependent_jobs:
            self.job_store.jobs[job_id]['created_at'] = old_date

        # Cleanup should handle dependencies
        old_jobs = self.job_store.get_jobs_older_than(7)
        assert len(old_jobs) == 4, f"Expected 4 old jobs, found {len(old_jobs)}"

        # Find parent jobs and their dependencies
        parent_jobs = [job for job in old_jobs if 'dependencies' in job['data']]
        dependent_job_ids = []

        for parent in parent_jobs:
            dependent_job_ids.extend(parent['data']['dependencies'])

        # Cleanup dependencies first, then parent
        for dep_id in dependent_job_ids:
            self.job_store.delete_job(dep_id)

        for parent in parent_jobs:
            self.job_store.delete_job(parent['id'])

        # Verify all jobs are cleaned
        remaining_jobs = len(self.job_store.jobs)
        assert remaining_jobs == 0, f"Expected 0 remaining jobs, found {remaining_jobs}"


class TestResourceCleanup:
    """Test cleanup of resources associated with jobs."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.job_store = MockJobStore()

    def teardown_method(self):
        """Cleanup test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_cleanup_temporary_files(self):
        """Test cleanup of temporary files created during job processing."""
        # Create temporary files for various jobs
        temp_files = []

        for i in range(5):
            temp_file = Path(self.temp_dir) / f"temp_processing_{i}.json"
            temp_file.write_text(json.dumps({'processing_data': i}))
            temp_files.append(temp_file)

            # Track file in job
            job_id = f"file_job_{i}"
            self.job_store.add_job(job_id, {
                'type': 'lc_validation',
                'temp_files': [str(temp_file)]
            }, 'completed')

        # Verify files exist
        assert all(f.exists() for f in temp_files), "Not all temp files created"

        # Cleanup temp files for completed jobs
        completed_jobs = [job for job in self.job_store.jobs.values() if job['status'] == 'completed']

        cleaned_files = 0
        for job in completed_jobs:
            temp_file_paths = job['data'].get('temp_files', [])
            for file_path in temp_file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_files += 1

        assert cleaned_files == 5, f"Expected to clean 5 files, cleaned {cleaned_files}"

        # Verify files are gone
        remaining_files = [f for f in temp_files if f.exists()]
        assert len(remaining_files) == 0, f"Expected 0 remaining files, found {len(remaining_files)}"

    def test_cleanup_memory_resources(self):
        """Test cleanup of memory resources and caches."""
        # Mock memory cache
        job_cache = {}
        result_cache = {}

        # Populate caches with job data
        for i in range(10):
            job_id = f"cached_job_{i}"
            job_cache[job_id] = {'data': f'large_data_{i}' * 1000}  # Simulate large data
            result_cache[job_id] = {'result': f'result_{i}'}

            self.job_store.add_job(job_id, {'type': 'lc_validation'}, 'completed')

        # Make some jobs old
        old_job_ids = []
        for i in range(0, 5):  # First 5 jobs are old
            job_id = f"cached_job_{i}"
            old_date = datetime.now() - timedelta(days=8)
            self.job_store.jobs[job_id]['created_at'] = old_date
            old_job_ids.append(job_id)

        # Cleanup memory for old jobs
        old_jobs = self.job_store.get_jobs_older_than(7)
        cleaned_cache_entries = 0

        for job in old_jobs:
            job_id = job['id']
            if job_id in job_cache:
                del job_cache[job_id]
                cleaned_cache_entries += 1
            if job_id in result_cache:
                del result_cache[job_id]
                cleaned_cache_entries += 1

        assert cleaned_cache_entries == 10, f"Expected to clean 10 cache entries, cleaned {cleaned_cache_entries}"

        # Verify recent jobs remain in cache
        remaining_job_cache = len(job_cache)
        remaining_result_cache = len(result_cache)

        assert remaining_job_cache == 5, f"Expected 5 job cache entries to remain"
        assert remaining_result_cache == 5, f"Expected 5 result cache entries to remain"

    def test_cleanup_database_connections(self):
        """Test cleanup of database connections from completed jobs."""
        # Mock database connection pool
        connection_pool = {}
        active_connections = {}

        # Create connections for jobs
        for i in range(8):
            job_id = f"db_job_{i}"
            connection_id = f"conn_{i}"

            connection_pool[connection_id] = {
                'job_id': job_id,
                'created_at': time.time(),
                'active': True
            }

            active_connections[job_id] = connection_id

            self.job_store.add_job(job_id, {
                'type': 'lc_validation',
                'connection_id': connection_id
            }, 'completed')

        # Make some jobs old
        for i in range(0, 4):  # First 4 jobs are old
            job_id = f"db_job_{i}"
            old_date = datetime.now() - timedelta(days=10)
            self.job_store.jobs[job_id]['created_at'] = old_date

        # Cleanup connections for old jobs
        old_jobs = self.job_store.get_jobs_older_than(7)
        closed_connections = 0

        for job in old_jobs:
            connection_id = job['data'].get('connection_id')
            if connection_id and connection_id in connection_pool:
                # "Close" the connection
                connection_pool[connection_id]['active'] = False
                del active_connections[job['id']]
                closed_connections += 1

        assert closed_connections == 4, f"Expected to close 4 connections, closed {closed_connections}"

        # Verify recent connections remain active
        active_count = len(active_connections)
        assert active_count == 4, f"Expected 4 active connections to remain"


class TestCleanupScheduling:
    """Test cleanup job scheduling and automation."""

    def test_scheduled_cleanup_execution(self):
        """Test that cleanup runs on schedule."""
        cleanup_executions = []
        last_cleanup_time = None

        def mock_cleanup_job():
            """Mock cleanup job execution."""
            nonlocal last_cleanup_time
            current_time = time.time()
            cleanup_executions.append(current_time)
            last_cleanup_time = current_time
            return len(cleanup_executions)

        # Simulate cleanup scheduling (every 24 hours)
        cleanup_interval = 24 * 3600  # 24 hours in seconds

        # Mock multiple cleanup executions
        base_time = time.time()
        scheduled_times = [
            base_time,
            base_time + cleanup_interval,
            base_time + (2 * cleanup_interval),
            base_time + (3 * cleanup_interval)
        ]

        for scheduled_time in scheduled_times:
            # Check if it's time for cleanup
            if last_cleanup_time is None or (scheduled_time - last_cleanup_time) >= cleanup_interval:
                with patch('time.time', return_value=scheduled_time):
                    execution_count = mock_cleanup_job()

        assert len(cleanup_executions) == 4, f"Expected 4 cleanup executions, got {len(cleanup_executions)}"

        # Verify cleanup intervals
        for i in range(1, len(cleanup_executions)):
            interval = cleanup_executions[i] - cleanup_executions[i-1]
            assert abs(interval - cleanup_interval) < 1, f"Cleanup interval incorrect: {interval}"

    def test_cleanup_failure_retry_logic(self):
        """Test retry logic when cleanup fails."""
        cleanup_attempts = []
        failure_count = 0

        def failing_cleanup_job():
            """Mock cleanup job that fails sometimes."""
            nonlocal failure_count
            cleanup_attempts.append(time.time())

            # Fail first 2 attempts, succeed on 3rd
            if len(cleanup_attempts) <= 2:
                failure_count += 1
                raise Exception(f"Cleanup failed (attempt {len(cleanup_attempts)})")

            return "success"

        # Retry logic: max 3 attempts with exponential backoff
        max_retries = 3
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                result = failing_cleanup_job()
                success = True
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    # Exponential backoff: 2^retry seconds
                    backoff_time = 2 ** retry_count
                    # In real implementation, would sleep here
                    pass
                else:
                    # Final failure
                    break

        assert success, "Cleanup should eventually succeed"
        assert len(cleanup_attempts) == 3, f"Expected 3 cleanup attempts, got {len(cleanup_attempts)}"
        assert failure_count == 2, f"Expected 2 failures before success, got {failure_count}"

    def test_concurrent_cleanup_prevention(self):
        """Test that concurrent cleanup processes don't interfere."""
        cleanup_lock = threading.Lock()
        active_cleanups = []

        def cleanup_process(process_id):
            """Mock cleanup process with locking."""
            if cleanup_lock.acquire(blocking=False):
                try:
                    active_cleanups.append(process_id)
                    # Simulate cleanup work
                    time.sleep(0.1)
                    return f"Process {process_id} completed cleanup"
                finally:
                    cleanup_lock.release()
            else:
                return f"Process {process_id} skipped (cleanup in progress)"

        # Start multiple cleanup processes concurrently
        threads = []
        results = {}

        for i in range(5):
            thread = threading.Thread(
                target=lambda pid=i: results.update({pid: cleanup_process(pid)})
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Only one process should have completed cleanup
        completed_processes = [r for r in results.values() if "completed cleanup" in r]
        skipped_processes = [r for r in results.values() if "skipped" in r]

        assert len(completed_processes) == 1, f"Expected 1 completed cleanup, got {len(completed_processes)}"
        assert len(skipped_processes) == 4, f"Expected 4 skipped cleanups, got {len(skipped_processes)}"

        # Only one process should have been active
        assert len(active_cleanups) == 1, f"Expected 1 active cleanup, got {len(active_cleanups)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])