#!/usr/bin/env python3
"""
Comprehensive tests for AWS Textract Fallback OCR System
Tests resilience, cost guardrails, and integration.
"""

import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ocr.textract_fallback import (
    TextractFallback, TextractResult, CostGuardrailError,
    TextractFallbackError, normalize_textract_output, process_with_fallback
)

class TestTextractFallback(unittest.TestCase):
    """Test AWS Textract fallback system"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "test_config.yaml"
        self.sample_pdf = self.test_dir / "sample.pdf"
        self.sample_image = self.test_dir / "sample.jpg"

        # Create test config
        self._create_test_config()

        # Create sample files
        self._create_sample_files()

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def _create_test_config(self):
        """Create test configuration file"""
        config_content = """
ocr:
  textract_fallback:
    enabled: true
    aws_region: "us-east-1"
    max_pages_per_day: 100
    max_pages_per_document: 20
    timeout_seconds: 30
    retry_attempts: 3
    features:
      - "TABLES"
      - "FORMS"
"""
        with open(self.config_file, 'w') as f:
            f.write(config_content)

    def _create_sample_files(self):
        """Create sample test files"""
        # Create dummy PDF (minimal valid PDF)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000100 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
179
%%EOF"""
        with open(self.sample_pdf, 'wb') as f:
            f.write(pdf_content)

        # Create dummy JPEG (1x1 pixel)
        jpeg_content = bytes.fromhex('FFD8FFE000104A46494600010101006000600000FFDB004300080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C2837292C30313434341F27393D38323C2E333432FFD9')
        with open(self.sample_image, 'wb') as f:
            f.write(jpeg_content)

    @patch('boto3.client')
    def test_initialization_success(self, mock_boto_client):
        """Test successful initialization"""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        textract = TextractFallback(str(self.config_file))

        self.assertIsNotNone(textract.textract_client)
        self.assertEqual(textract.config.aws_region, "us-east-1")
        self.assertEqual(textract.config.max_pages_per_day, 100)
        mock_boto_client.assert_called_with('textract', region_name='us-east-1')

    @patch('boto3.client')
    def test_initialization_failure(self, mock_boto_client):
        """Test initialization failure handling"""
        mock_boto_client.side_effect = Exception("AWS credentials not found")

        with self.assertRaises(TextractFallbackError):
            TextractFallback(str(self.config_file))

    @patch('boto3.client')
    def test_document_validation(self, mock_boto_client):
        """Test document validation checks"""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        textract = TextractFallback(str(self.config_file))

        # Test non-existent file
        with self.assertRaises(TextractFallbackError) as cm:
            textract._validate_document("/non/existent/file.pdf")
        self.assertIn("Document not found", str(cm.exception))

        # Test unsupported format
        unsupported_file = self.test_dir / "test.txt"
        unsupported_file.write_text("test content")

        with self.assertRaises(TextractFallbackError) as cm:
            textract._validate_document(str(unsupported_file))
        self.assertIn("Unsupported format", str(cm.exception))

        # Test valid file - should not raise exception
        textract._validate_document(str(self.sample_pdf))

    @patch('boto3.client')
    @patch('ocr.textract_fallback.TextractUsageTracker')
    def test_cost_guardrails(self, mock_tracker_class, mock_boto_client):
        """Test cost guardrail enforcement"""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        textract = TextractFallback(str(self.config_file))

        # Test page limit exceeded
        mock_tracker.get_daily_usage.return_value = {'pages': 150, 'cost': 50.0}

        with self.assertRaises(CostGuardrailError) as cm:
            textract._check_cost_guardrails()
        self.assertIn("Daily page limit exceeded", str(cm.exception))

        # Test cost limit exceeded
        mock_tracker.get_daily_usage.return_value = {'pages': 50, 'cost': 150.0}

        with self.assertRaises(CostGuardrailError) as cm:
            textract._check_cost_guardrails()
        self.assertIn("Daily cost limit exceeded", str(cm.exception))

        # Test within limits - should not raise exception
        mock_tracker.get_daily_usage.return_value = {'pages': 50, 'cost': 50.0}
        textract._check_cost_guardrails()

    @patch('boto3.client')
    def test_sync_processing_success(self, mock_boto_client):
        """Test successful synchronous processing"""
        mock_textract_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_boto_client.side_effect = lambda service, **kwargs: {
            'textract': mock_textract_client,
            's3': mock_s3_client
        }[service]

        # Mock Textract response
        mock_textract_response = {
            'Blocks': [
                {
                    'BlockType': 'PAGE',
                    'Id': 'page-1',
                    'Confidence': 99.5
                },
                {
                    'BlockType': 'LINE',
                    'Id': 'line-1',
                    'Text': 'Sample LC Document',
                    'Confidence': 95.0
                },
                {
                    'BlockType': 'LINE',
                    'Id': 'line-2',
                    'Text': 'Amount: USD 100,000',
                    'Confidence': 98.0
                }
            ]
        }
        mock_textract_client.analyze_document.return_value = mock_textract_response

        # Mock usage tracker
        with patch('ocr.textract_fallback.TextractUsageTracker') as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_daily_usage.return_value = {'pages': 10, 'cost': 15.0}
            mock_tracker_class.return_value = mock_tracker

            textract = TextractFallback(str(self.config_file))
            result = textract.process_document(str(self.sample_pdf), "test-job-123")

            # Verify result
            self.assertIsInstance(result, TextractResult)
            self.assertIn('Sample LC Document', result.text)
            self.assertIn('Amount: USD 100,000', result.text)
            self.assertEqual(result.pages, 1)
            self.assertGreater(result.confidence, 90)
            self.assertEqual(result.job_id, "test-job-123")

            # Verify usage tracking
            mock_tracker.record_usage.assert_called_once()

    @patch('boto3.client')
    def test_sync_processing_failure(self, mock_boto_client):
        """Test synchronous processing failure"""
        mock_textract_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_boto_client.side_effect = lambda service, **kwargs: {
            'textract': mock_textract_client,
            's3': mock_s3_client
        }[service]

        mock_textract_client.analyze_document.side_effect = Exception("Textract API error")

        with patch('ocr.textract_fallback.TextractUsageTracker') as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_daily_usage.return_value = {'pages': 10, 'cost': 15.0}
            mock_tracker_class.return_value = mock_tracker

            textract = TextractFallback(str(self.config_file))

            with self.assertRaises(TextractFallbackError) as cm:
                textract.process_document(str(self.sample_pdf), "test-job-fail")
            self.assertIn("Document processing failed", str(cm.exception))

    @patch('boto3.client')
    @patch('time.sleep')  # Speed up test by mocking sleep
    def test_async_processing_success(self, mock_sleep, mock_boto_client):
        """Test successful asynchronous processing"""
        mock_textract_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_boto_client.side_effect = lambda service, **kwargs: {
            'textract': mock_textract_client,
            's3': mock_s3_client
        }[service]

        # Mock S3 upload
        mock_s3_client.upload_file.return_value = None

        # Mock start async job
        mock_textract_client.start_document_analysis.return_value = {
            'JobId': 'textract-job-123'
        }

        # Mock job completion
        completed_response = {
            'JobStatus': 'SUCCEEDED',
            'Blocks': [
                {
                    'BlockType': 'PAGE',
                    'Id': 'page-1',
                    'Confidence': 99.0
                },
                {
                    'BlockType': 'LINE',
                    'Id': 'line-1',
                    'Text': 'Large LC Document',
                    'Confidence': 97.0
                }
            ]
        }
        mock_textract_client.get_document_analysis.return_value = completed_response

        with patch('ocr.textract_fallback.TextractUsageTracker') as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_daily_usage.return_value = {'pages': 10, 'cost': 15.0}
            mock_tracker_class.return_value = mock_tracker

            textract = TextractFallback(str(self.config_file))

            # Create large file to trigger async processing
            large_file = self.test_dir / "large.pdf"
            with open(large_file, 'wb') as f:
                f.write(b"x" * (60 * 1024 * 1024))  # 60MB file

            with patch.object(textract, '_is_large_document', return_value=True):
                result = textract.process_document(str(large_file), "async-job-123")

            # Verify result
            self.assertIsInstance(result, TextractResult)
            self.assertIn('Large LC Document', result.text)
            self.assertEqual(result.job_id, "async-job-123")

            # Verify AWS calls
            mock_s3_client.upload_file.assert_called_once()
            mock_textract_client.start_document_analysis.assert_called_once()
            mock_textract_client.get_document_analysis.assert_called()

    def test_normalize_textract_output(self):
        """Test output normalization for pipeline compatibility"""
        textract_result = TextractResult(
            text="LC Number: LC-2024-001\nAmount: USD 50,000",
            confidence=95.5,
            tables=[],
            forms=[],
            pages=2,
            cost_estimate=0.003,
            processing_time=15.5,
            job_id="test-job-normalize"
        )

        normalized = normalize_textract_output(textract_result)

        # Verify structure
        self.assertIn('extracted_text', normalized)
        self.assertIn('confidence_score', normalized)
        self.assertIn('pages_processed', normalized)
        self.assertIn('metadata', normalized)

        # Verify content
        self.assertEqual(normalized['extracted_text'], textract_result.text)
        self.assertAlmostEqual(normalized['confidence_score'], 0.955, places=3)
        self.assertEqual(normalized['pages_processed'], 2)
        self.assertEqual(normalized['metadata']['processing_method'], 'aws_textract')
        self.assertEqual(normalized['metadata']['job_id'], "test-job-normalize")

    @patch('boto3.client')
    def test_process_with_fallback_skip(self, mock_boto_client):
        """Test fallback skipped when primary OCR succeeds"""
        primary_result = {
            'extracted_text': 'High quality OCR result',
            'confidence_score': 0.85,
            'processing_method': 'primary_ocr'
        }

        result = process_with_fallback(str(self.sample_pdf), primary_result)

        # Should return primary result unchanged
        self.assertEqual(result, primary_result)

    @patch('boto3.client')
    def test_process_with_fallback_triggered(self, mock_boto_client):
        """Test fallback triggered when primary OCR fails"""
        mock_textract_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_boto_client.side_effect = lambda service, **kwargs: {
            'textract': mock_textract_client,
            's3': mock_s3_client
        }[service]

        # Mock successful Textract response
        mock_textract_response = {
            'Blocks': [
                {
                    'BlockType': 'PAGE',
                    'Id': 'page-1',
                    'Confidence': 98.0
                },
                {
                    'BlockType': 'LINE',
                    'Id': 'line-1',
                    'Text': 'Fallback OCR result',
                    'Confidence': 92.0
                }
            ]
        }
        mock_textract_client.analyze_document.return_value = mock_textract_response

        # Poor quality primary result should trigger fallback
        primary_result = {
            'extracted_text': 'Poor quality result',
            'confidence_score': 0.45,
            'processing_method': 'primary_ocr'
        }

        with patch('ocr.textract_fallback.TextractUsageTracker') as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.get_daily_usage.return_value = {'pages': 10, 'cost': 15.0}
            mock_tracker_class.return_value = mock_tracker

            result = process_with_fallback(str(self.sample_pdf), primary_result)

            # Should return Textract result
            self.assertIn('Fallback OCR result', result['extracted_text'])
            self.assertEqual(result['metadata']['processing_method'], 'aws_textract')

    def test_table_extraction(self):
        """Test table extraction from Textract blocks"""
        with patch('boto3.client'):
            textract = TextractFallback(str(self.config_file))

            # Mock blocks with table data
            blocks = [
                {
                    'BlockType': 'TABLE',
                    'Id': 'table-1',
                    'Confidence': 95.0,
                    'Geometry': {'BoundingBox': {'Width': 0.8, 'Height': 0.3}},
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['cell-1', 'cell-2']
                        }
                    ]
                },
                {
                    'BlockType': 'CELL',
                    'Id': 'cell-1',
                    'RowIndex': 1,
                    'ColumnIndex': 1,
                    'Confidence': 90.0,
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['word-1']
                        }
                    ]
                },
                {
                    'BlockType': 'CELL',
                    'Id': 'cell-2',
                    'RowIndex': 1,
                    'ColumnIndex': 2,
                    'Confidence': 88.0,
                    'Relationships': [
                        {
                            'Type': 'CHILD',
                            'Ids': ['word-2']
                        }
                    ]
                },
                {
                    'BlockType': 'WORD',
                    'Id': 'word-1',
                    'Text': 'Amount',
                    'Confidence': 90.0
                },
                {
                    'BlockType': 'WORD',
                    'Id': 'word-2',
                    'Text': 'USD 100,000',
                    'Confidence': 88.0
                }
            ]

            tables = textract._extract_tables(blocks)

            self.assertEqual(len(tables), 1)
            table = tables[0]
            self.assertEqual(table['id'], 'table-1')
            self.assertEqual(table['confidence'], 95.0)
            self.assertIn('rows', table)

    def test_usage_tracking(self):
        """Test usage tracking functionality"""
        from ocr.textract_fallback import TextractUsageTracker

        # Use temporary file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = TextractUsageTracker()
            tracker.usage_file = Path(temp_dir) / "test_usage.json"

            # Record usage
            tracker.record_usage(5, 7.5)
            tracker.record_usage(3, 4.5)

            # Check daily usage
            daily_usage = tracker.get_daily_usage()
            self.assertEqual(daily_usage['pages'], 8)
            self.assertEqual(daily_usage['cost'], 12.0)

            # Check monthly usage
            monthly_usage = tracker.get_monthly_usage()
            self.assertEqual(monthly_usage['pages'], 8)
            self.assertEqual(monthly_usage['cost'], 12.0)

    def test_config_loading_fallback(self):
        """Test configuration loading with fallback to defaults"""
        with patch('boto3.client'):
            # Test with non-existent config file
            textract = TextractFallback("/non/existent/config.yaml")

            # Should use default configuration
            self.assertEqual(textract.config.aws_region, 'us-east-1')
            self.assertEqual(textract.config.max_pages_per_day, 1000)
            self.assertIn('TABLES', textract.config.features)

def run_textract_tests():
    """Run comprehensive Textract fallback tests"""
    print("🧪 Running AWS Textract Fallback Tests")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTextractFallback)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n📊 Test Summary:")
    print(f"  • Tests Run: {result.testsRun}")
    print(f"  • Failures: {len(result.failures)}")
    print(f"  • Errors: {len(result.errors)}")
    print(f"  • Skipped: {len(result.skipped)}")

    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Error:')[-1].strip()}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All Tests Passed!' if success else '❌ Some Tests Failed'}")

    return success

if __name__ == "__main__":
    success = run_textract_tests()
    sys.exit(0 if success else 1)