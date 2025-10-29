#!/usr/bin/env python3
"""
Security Tests - File Upload Validation
Tests that file uploads are properly validated and limited to 10MB
"""

import unittest
import os
import sys
import tempfile
from io import BytesIO
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestFileUploadSecurity(unittest.TestCase):
    """Test file upload security validation"""

    def setUp(self):
        """Set up test environment"""
        # Import Flask app
        from sme_portal.app import app
        self.app = app
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    def test_max_content_length_configured(self):
        """Test that MAX_CONTENT_LENGTH is properly configured"""
        # Check that MAX_CONTENT_LENGTH is set to 10MB
        self.assertEqual(self.app.config['MAX_CONTENT_LENGTH'], 10 * 1024 * 1024)

    def test_file_too_large_rejected(self):
        """Test that files over 10MB are rejected"""
        # Create a file larger than 10MB (11MB)
        large_data = b'X' * (11 * 1024 * 1024)
        large_file = BytesIO(large_data)

        with self.client as client:
            # Attempt to upload large file
            response = client.post('/validate',
                data={
                    'lc_file': (large_file, 'large_document.pdf'),
                    'lc_number': 'LC123456',
                    'applicant_name': 'Test Company',
                    'beneficiary_name': 'Beneficiary Co',
                    'issuing_bank': 'Test Bank',
                    'lc_amount': '100000',
                    'lc_currency': 'USD'
                },
                content_type='multipart/form-data',
                follow_redirects=False
            )

            # Should return 413 Request Entity Too Large
            self.assertEqual(response.status_code, 413)

    def test_file_under_limit_accepted(self):
        """Test that files under 10MB are accepted"""
        # Create a file under 10MB (5MB)
        normal_data = b'X' * (5 * 1024 * 1024)
        normal_file = BytesIO(normal_data)

        with patch('sme_portal.app.validate_lc_document') as mock_validate:
            mock_validate.return_value = ({'status': 'valid'}, 200)

            with self.client as client:
                response = client.post('/validate',
                    data={
                        'lc_file': (normal_file, 'normal_document.pdf'),
                        'lc_number': 'LC123456',
                        'applicant_name': 'Test Company',
                        'beneficiary_name': 'Beneficiary Co',
                        'issuing_bank': 'Test Bank',
                        'lc_amount': '100000',
                        'lc_currency': 'USD'
                    },
                    content_type='multipart/form-data',
                    follow_redirects=False
                )

                # Should not return 413
                self.assertNotEqual(response.status_code, 413)

    def test_explicit_size_check_in_route(self):
        """Test that the route explicitly checks file size"""
        # Create a mock file with size attribute
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = 'test.pdf'
        mock_file.read.return_value = b'test data'
        mock_file.seek = MagicMock()
        mock_file.tell.return_value = 11 * 1024 * 1024  # 11MB

        with patch('sme_portal.app.request') as mock_request:
            mock_request.files = {'lc_file': mock_file}
            mock_request.form = {
                'lc_number': 'LC123456',
                'applicant_name': 'Test Company',
                'beneficiary_name': 'Beneficiary Co',
                'issuing_bank': 'Test Bank',
                'lc_amount': '100000',
                'lc_currency': 'USD'
            }

            with self.client as client:
                response = client.post('/validate', follow_redirects=True)

                # Check that file size validation occurs
                # The response should redirect with an error message
                self.assertIn(b'error', response.data.lower())

    def test_error_handler_413(self):
        """Test that 413 error handler is properly configured"""
        from sme_portal.app import request_entity_too_large

        # Create a mock error
        mock_error = MagicMock()
        mock_error.code = 413

        with self.app.test_request_context():
            # Call the error handler
            response = request_entity_too_large(mock_error)

            # Should redirect to validate_lc
            self.assertEqual(response.status_code, 302)
            self.assertIn('/validate', response.location)

    def test_file_size_boundary_conditions(self):
        """Test file size at exactly 10MB boundary"""
        # Test file exactly at 10MB
        exact_limit_data = b'X' * (10 * 1024 * 1024)
        exact_file = BytesIO(exact_limit_data)

        with patch('sme_portal.app.validate_lc_document') as mock_validate:
            mock_validate.return_value = ({'status': 'valid'}, 200)

            with self.client as client:
                response = client.post('/validate',
                    data={
                        'lc_file': (exact_file, 'exact_limit.pdf'),
                        'lc_number': 'LC123456',
                        'applicant_name': 'Test Company',
                        'beneficiary_name': 'Beneficiary Co',
                        'issuing_bank': 'Test Bank',
                        'lc_amount': '100000',
                        'lc_currency': 'USD'
                    },
                    content_type='multipart/form-data',
                    follow_redirects=False
                )

                # File at exactly 10MB should be accepted
                self.assertNotEqual(response.status_code, 413)

        # Test file at 10MB + 1 byte
        over_limit_data = b'X' * (10 * 1024 * 1024 + 1)
        over_file = BytesIO(over_limit_data)

        with self.client as client:
            response = client.post('/validate',
                data={
                    'lc_file': (over_file, 'over_limit.pdf'),
                    'lc_number': 'LC123456',
                    'applicant_name': 'Test Company',
                    'beneficiary_name': 'Beneficiary Co',
                    'issuing_bank': 'Test Bank',
                    'lc_amount': '100000',
                    'lc_currency': 'USD'
                },
                content_type='multipart/form-data',
                follow_redirects=False
            )

            # File over 10MB should be rejected
            self.assertEqual(response.status_code, 413)

    def test_multiple_file_upload_attempts(self):
        """Test that multiple file upload attempts are properly validated"""
        # First attempt with large file
        large_data = b'X' * (15 * 1024 * 1024)
        large_file = BytesIO(large_data)

        with self.client as client:
            response1 = client.post('/validate',
                data={'lc_file': (large_file, 'large.pdf')},
                content_type='multipart/form-data',
                follow_redirects=False
            )
            self.assertEqual(response1.status_code, 413)

            # Second attempt with normal file should work
            normal_data = b'Y' * (1 * 1024 * 1024)
            normal_file = BytesIO(normal_data)

            with patch('sme_portal.app.validate_lc_document') as mock_validate:
                mock_validate.return_value = ({'status': 'valid'}, 200)

                response2 = client.post('/validate',
                    data={
                        'lc_file': (normal_file, 'normal.pdf'),
                        'lc_number': 'LC123456',
                        'applicant_name': 'Test Company',
                        'beneficiary_name': 'Beneficiary Co',
                        'issuing_bank': 'Test Bank',
                        'lc_amount': '100000',
                        'lc_currency': 'USD'
                    },
                    content_type='multipart/form-data',
                    follow_redirects=False
                )
                self.assertNotEqual(response2.status_code, 413)

    def test_file_extension_validation(self):
        """Test that only allowed file extensions are accepted"""
        # Test with allowed extension (.pdf)
        pdf_data = b'PDF content'
        pdf_file = BytesIO(pdf_data)

        with patch('sme_portal.app.validate_lc_document') as mock_validate:
            mock_validate.return_value = ({'status': 'valid'}, 200)

            with self.client as client:
                response = client.post('/validate',
                    data={
                        'lc_file': (pdf_file, 'document.pdf'),
                        'lc_number': 'LC123456',
                        'applicant_name': 'Test Company',
                        'beneficiary_name': 'Beneficiary Co',
                        'issuing_bank': 'Test Bank',
                        'lc_amount': '100000',
                        'lc_currency': 'USD'
                    },
                    content_type='multipart/form-data',
                    follow_redirects=True
                )

                # PDF should be accepted
                self.assertNotIn(b'Invalid file type', response.data)

        # Test with disallowed extension (.exe)
        exe_data = b'EXE content'
        exe_file = BytesIO(exe_data)

        with self.client as client:
            response = client.post('/validate',
                data={
                    'lc_file': (exe_file, 'malware.exe'),
                    'lc_number': 'LC123456',
                    'applicant_name': 'Test Company',
                    'beneficiary_name': 'Beneficiary Co',
                    'issuing_bank': 'Test Bank',
                    'lc_amount': '100000',
                    'lc_currency': 'USD'
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )

            # EXE should be rejected
            self.assertIn(b'Invalid file type', response.data)


if __name__ == '__main__':
    unittest.main()