"""
Document Validation Metrics and Monitoring System
Provides comprehensive metrics collection for document validation rejection rates
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time
from collections import defaultdict, deque


logger = logging.getLogger(__name__)


@dataclass
class ValidationMetric:
    """Single validation attempt metric"""
    timestamp: datetime
    request_id: Optional[str]
    user_type: str
    workflow_type: str
    file_count: int
    total_size_mb: float

    # File type validation results
    invalid_file_types: List[str]  # List of rejected file extensions
    file_type_rejections: int

    # Content validation results
    invalid_document_content: List[Dict]  # Details of content validation failures
    content_rejections: int
    suspicious_content_detections: int

    # Overall outcome
    validation_passed: bool
    processing_time_ms: float

    # Cost protection metrics
    ocr_processing_prevented: bool  # True if rejection prevented OCR cost
    llm_processing_prevented: bool  # True if rejection prevented LLM cost
    estimated_cost_savings: float  # Estimated USD savings from early rejection


class ValidationMetricsCollector:
    """Collects and analyzes document validation metrics"""

    def __init__(self, metrics_file: Optional[str] = None):
        self.metrics_file = metrics_file or "validation_metrics.jsonl"
        self.metrics_lock = threading.Lock()

        # In-memory metrics for real-time analysis
        self.recent_metrics = deque(maxlen=1000)  # Last 1000 validations

        # Aggregated statistics
        self.hourly_stats = defaultdict(lambda: defaultdict(int))
        self.daily_stats = defaultdict(lambda: defaultdict(int))

        # Cost estimates (USD per operation)
        self.OCR_COST_PER_PAGE = 0.0015  # Average OCR cost
        self.LLM_COST_PER_REQUEST = 0.002  # Average LLM processing cost

    def record_validation_attempt(
        self,
        request_id: Optional[str],
        user_type: str,
        workflow_type: str,
        files: List[Any],
        validation_results: List[Dict],
        validation_passed: bool,
        processing_time_ms: float
    ) -> ValidationMetric:
        """Record a validation attempt with full details"""

        # Calculate file metrics
        file_count = len(files)
        total_size_mb = sum(getattr(f, 'size', 0) for f in files) / (1024 * 1024)

        # Analyze validation results
        invalid_file_types = []
        invalid_content = []
        file_type_rejections = 0
        content_rejections = 0
        suspicious_content_detections = 0

        for result in validation_results:
            error_type = result.get('error_type', '')
            if error_type == 'invalid_file_type':
                file_type_rejections += 1
                # Extract file extension from error message
                file_name = result.get('file', '')
                if file_name:
                    ext = Path(file_name).suffix
                    if ext:
                        invalid_file_types.append(ext)
            elif error_type == 'invalid_document_content':
                content_rejections += 1
                invalid_content.append({
                    'file': result.get('file', ''),
                    'expected': result.get('expected', ''),
                    'actual': result.get('actual', ''),
                    'confidence': result.get('confidence', 0.0)
                })
            elif error_type == 'suspicious_content':
                suspicious_content_detections += 1
                invalid_content.append({
                    'file': result.get('file', ''),
                    'reason': 'suspicious_content',
                    'confidence': result.get('confidence', 0.0)
                })

        # Calculate cost protection benefits
        ocr_prevented = not validation_passed and file_count > 0
        llm_prevented = not validation_passed and file_count > 0
        estimated_savings = 0.0

        if ocr_prevented:
            # Estimate 2 pages per PDF on average
            estimated_pages = file_count * 2
            estimated_savings += estimated_pages * self.OCR_COST_PER_PAGE

        if llm_prevented:
            estimated_savings += file_count * self.LLM_COST_PER_REQUEST

        # Create metric record
        metric = ValidationMetric(
            timestamp=datetime.now(timezone.utc),
            request_id=request_id,
            user_type=user_type,
            workflow_type=workflow_type,
            file_count=file_count,
            total_size_mb=total_size_mb,
            invalid_file_types=invalid_file_types,
            file_type_rejections=file_type_rejections,
            invalid_document_content=invalid_content,
            content_rejections=content_rejections,
            suspicious_content_detections=suspicious_content_detections,
            validation_passed=validation_passed,
            processing_time_ms=processing_time_ms,
            ocr_processing_prevented=ocr_prevented,
            llm_processing_prevented=llm_prevented,
            estimated_cost_savings=estimated_savings
        )

        # Store metric
        self._store_metric(metric)

        # Update statistics
        self._update_statistics(metric)

        # Log important events
        self._log_metric(metric)

        return metric

    def _store_metric(self, metric: ValidationMetric):
        """Store metric to file and memory"""
        with self.metrics_lock:
            # Add to recent metrics
            self.recent_metrics.append(metric)

            # Write to file
            try:
                with open(self.metrics_file, 'a') as f:
                    # Convert datetime to string for JSON serialization
                    metric_dict = asdict(metric)
                    metric_dict['timestamp'] = metric.timestamp.isoformat()
                    f.write(json.dumps(metric_dict) + '\n')
            except Exception as e:
                logger.error(f"Failed to write metric to file: {e}")

    def _update_statistics(self, metric: ValidationMetric):
        """Update hourly and daily statistics"""
        hour_key = metric.timestamp.strftime('%Y-%m-%d-%H')
        day_key = metric.timestamp.strftime('%Y-%m-%d')

        # Update hourly stats
        self.hourly_stats[hour_key]['total_validations'] += 1
        self.hourly_stats[hour_key]['files_processed'] += metric.file_count
        self.hourly_stats[hour_key]['total_size_mb'] += metric.total_size_mb

        if not metric.validation_passed:
            self.hourly_stats[hour_key]['rejections'] += 1
            self.hourly_stats[hour_key]['cost_savings_usd'] += metric.estimated_cost_savings

        self.hourly_stats[hour_key]['file_type_rejections'] += metric.file_type_rejections
        self.hourly_stats[hour_key]['content_rejections'] += metric.content_rejections
        self.hourly_stats[hour_key]['suspicious_detections'] += metric.suspicious_content_detections

        # Update daily stats (similar logic)
        self.daily_stats[day_key]['total_validations'] += 1
        self.daily_stats[day_key]['files_processed'] += metric.file_count

        if not metric.validation_passed:
            self.daily_stats[day_key]['rejections'] += 1
            self.daily_stats[day_key]['cost_savings_usd'] += metric.estimated_cost_savings

    def _log_metric(self, metric: ValidationMetric):
        """Log important validation events"""
        if not metric.validation_passed:
            rejection_reasons = []
            if metric.file_type_rejections > 0:
                rejection_reasons.append(f"{metric.file_type_rejections} invalid file types: {metric.invalid_file_types}")
            if metric.content_rejections > 0:
                rejection_reasons.append(f"{metric.content_rejections} content validation failures")
            if metric.suspicious_content_detections > 0:
                rejection_reasons.append(f"{metric.suspicious_content_detections} suspicious content detections")

            logger.warning(
                f"Document validation REJECTED - "
                f"Request: {metric.request_id}, "
                f"User: {metric.user_type}, "
                f"Workflow: {metric.workflow_type}, "
                f"Files: {metric.file_count}, "
                f"Reasons: {'; '.join(rejection_reasons)}, "
                f"Cost savings: ${metric.estimated_cost_savings:.4f}"
            )
        else:
            logger.info(
                f"Document validation PASSED - "
                f"Request: {metric.request_id}, "
                f"Files: {metric.file_count}, "
                f"Time: {metric.processing_time_ms:.1f}ms"
            )

    def get_rejection_rates(self, hours: int = 24) -> Dict[str, Any]:
        """Get rejection rates for the last N hours"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        recent_validations = [
            m for m in self.recent_metrics
            if m.timestamp.timestamp() > cutoff_time
        ]

        if not recent_validations:
            return {
                'period_hours': hours,
                'total_validations': 0,
                'rejection_rate': 0.0,
                'cost_savings_usd': 0.0
            }

        total = len(recent_validations)
        rejections = sum(1 for m in recent_validations if not m.validation_passed)
        total_savings = sum(m.estimated_cost_savings for m in recent_validations)

        # Breakdown by rejection type
        file_type_rejections = sum(m.file_type_rejections for m in recent_validations)
        content_rejections = sum(m.content_rejections for m in recent_validations)
        suspicious_detections = sum(m.suspicious_content_detections for m in recent_validations)

        # Most common invalid file types
        invalid_types = []
        for m in recent_validations:
            invalid_types.extend(m.invalid_file_types)

        from collections import Counter
        top_invalid_types = Counter(invalid_types).most_common(5)

        return {
            'period_hours': hours,
            'total_validations': total,
            'total_rejections': rejections,
            'rejection_rate': rejections / total if total > 0 else 0.0,
            'cost_savings_usd': total_savings,
            'breakdown': {
                'file_type_rejections': file_type_rejections,
                'content_rejections': content_rejections,
                'suspicious_content_detections': suspicious_detections
            },
            'top_invalid_file_types': top_invalid_types,
            'average_processing_time_ms': sum(m.processing_time_ms for m in recent_validations) / total
        }

    def get_workflow_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics broken down by workflow type"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (days * 24 * 3600)

        recent_validations = [
            m for m in self.recent_metrics
            if m.timestamp.timestamp() > cutoff_time
        ]

        workflow_stats = defaultdict(lambda: {
            'total_validations': 0,
            'rejections': 0,
            'files_processed': 0,
            'cost_savings_usd': 0.0
        })

        for metric in recent_validations:
            workflow = metric.workflow_type
            workflow_stats[workflow]['total_validations'] += 1
            workflow_stats[workflow]['files_processed'] += metric.file_count
            workflow_stats[workflow]['cost_savings_usd'] += metric.estimated_cost_savings

            if not metric.validation_passed:
                workflow_stats[workflow]['rejections'] += 1

        # Calculate rejection rates
        for workflow_data in workflow_stats.values():
            total = workflow_data['total_validations']
            workflow_data['rejection_rate'] = (
                workflow_data['rejections'] / total if total > 0 else 0.0
            )

        return {
            'period_days': days,
            'workflows': dict(workflow_stats)
        }

    def export_metrics_csv(self, output_file: str, hours: int = 168) -> str:
        """Export metrics to CSV for analysis"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        recent_validations = [
            m for m in self.recent_metrics
            if m.timestamp.timestamp() > cutoff_time
        ]

        import csv
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'request_id', 'user_type', 'workflow_type',
                'file_count', 'total_size_mb', 'validation_passed',
                'processing_time_ms', 'file_type_rejections', 'content_rejections',
                'suspicious_detections', 'cost_savings_usd', 'invalid_file_types'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for metric in recent_validations:
                writer.writerow({
                    'timestamp': metric.timestamp.isoformat(),
                    'request_id': metric.request_id,
                    'user_type': metric.user_type,
                    'workflow_type': metric.workflow_type,
                    'file_count': metric.file_count,
                    'total_size_mb': metric.total_size_mb,
                    'validation_passed': metric.validation_passed,
                    'processing_time_ms': metric.processing_time_ms,
                    'file_type_rejections': metric.file_type_rejections,
                    'content_rejections': metric.content_rejections,
                    'suspicious_detections': metric.suspicious_content_detections,
                    'cost_savings_usd': metric.estimated_cost_savings,
                    'invalid_file_types': ','.join(metric.invalid_file_types)
                })

        return f"Exported {len(recent_validations)} metrics to {output_file}"


# Global metrics collector instance
_metrics_collector: Optional[ValidationMetricsCollector] = None


def get_metrics_collector() -> ValidationMetricsCollector:
    """Get or create the global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = ValidationMetricsCollector()
    return _metrics_collector


def record_validation_metric(
    request_id: Optional[str],
    user_type: str,
    workflow_type: str,
    files: List[Any],
    validation_errors: List[Dict],
    validation_passed: bool,
    processing_time_ms: float
) -> ValidationMetric:
    """Convenience function to record a validation metric"""
    collector = get_metrics_collector()
    return collector.record_validation_attempt(
        request_id=request_id,
        user_type=user_type,
        workflow_type=workflow_type,
        files=files,
        validation_results=validation_errors,
        validation_passed=validation_passed,
        processing_time_ms=processing_time_ms
    )