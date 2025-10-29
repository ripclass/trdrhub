"""
Comprehensive unit tests for enhanced document validation layer
Tests all requirements including file-type guardrails and document classification
"""

import pytest
import json
import io
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from document_validator import DocumentValidator, DocumentType, ValidationResult


class TestDocumentValidator:
    """Test the DocumentValidator class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.validator = DocumentValidator()

    def test_file_type_validation_valid_pdf(self):
        """Test valid PDF file type validation"""
        # Create a simple PDF-like content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"

        is_valid, error = self.validator.validate_file_type(pdf_content, "test.pdf")
        assert is_valid is True
        assert error is None

    def test_file_type_validation_invalid_extension(self):
        """Test invalid file extension rejection"""
        content = b"some content"

        is_valid, error = self.validator.validate_file_type(content, "test.docx")
        assert is_valid is False
        assert "not supported" in error
        assert ".docx" in error

    def test_file_type_validation_file_too_large(self):
        """Test file size limit enforcement"""
        # Create content larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)

        is_valid, error = self.validator.validate_file_type(large_content, "test.pdf")
        assert is_valid is False
        assert "exceeds maximum" in error

    def test_extract_text_from_pdf_mock(self):
        """Test PDF text extraction (mocked)"""
        pdf_content = b"%PDF-1.4\nsome pdf content"

        with patch('document_validator.PyPDF2') as mock_pypdf:
            mock_reader = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Commercial Invoice\nInvoice No: 12345"
            mock_reader.pages = [mock_page]
            mock_pypdf.PdfReader.return_value = mock_reader

            text = self.validator.extract_text_content(pdf_content, "invoice.pdf")
            assert "commercial invoice" in text
            assert "invoice no" in text

    def test_document_classification_invoice_valid(self):
        """Test valid invoice document classification"""
        invoice_text = """
        Commercial Invoice
        Invoice No: COM-2024-001
        Invoice Date: 2024-01-15
        Seller: Export Company Ltd
        Buyer: Import Corp
        Total Amount: USD 50,000
        """

        result = self.validator.classify_document_type(invoice_text.lower(), DocumentType.INVOICE)

        assert result.result == ValidationResult.VALID
        assert result.confidence >= 0.3
        assert result.detected_type == DocumentType.INVOICE
        assert "commercial invoice" in result.keywords_found
        assert "invoice no" in result.keywords_found

    def test_document_classification_mismatch(self):
        """Test document type mismatch detection"""
        # CV content uploaded as invoice
        cv_text = """
        Curriculum Vitae
        John Doe
        Software Engineer
        Experience:
        - Software Development
        - Python Programming
        Education:
        - Computer Science Degree
        """

        result = self.validator.classify_document_type(cv_text.lower(), DocumentType.INVOICE)

        assert result.result == ValidationResult.SUSPICIOUS_CONTENT
        assert result.confidence > 0.7

    def test_document_classification_lc_valid(self):
        """Test valid LC document classification"""
        lc_text = """
        Letter of Credit
        LC No: LC-2024-BD-001
        Subject to UCP 600
        Irrevocable Documentary Credit
        Issuing Bank: Standard Bank
        Advising Bank: Commerce Bank
        Beneficiary: Global Exports Ltd
        Applicant: Local Imports Inc
        """

        result = self.validator.classify_document_type(lc_text.lower(), DocumentType.LC)

        assert result.result == ValidationResult.VALID
        assert result.confidence >= 0.3
        assert result.detected_type == DocumentType.LC
        assert len(result.keywords_found) >= 3

    def test_document_classification_bl_valid(self):
        """Test valid Bill of Lading classification"""
        bl_text = """
        Bill of Lading
        B/L No: BL-2024-001
        Shipper: Export Company Ltd
        Consignee: Import Company Ltd
        Notify Party: Freight Forwarder
        Port of Loading: Chittagong
        Port of Discharge: Hamburg
        Vessel: MV Trade Express
        Container No: TCLU-123456-7
        """

        result = self.validator.classify_document_type(bl_text.lower(), DocumentType.BILL_OF_LADING)

        assert result.result == ValidationResult.VALID
        assert result.confidence >= 0.3
        assert result.detected_type == DocumentType.BILL_OF_LADING

    def test_document_classification_bank_statement_as_invoice(self):
        """Test rejection of bank statement uploaded as invoice"""
        bank_statement_text = """
        Bank Statement
        Account No: 1234567890
        Balance: USD 10,000
        Transaction History:
        - Deposit: USD 5,000
        - Withdrawal: USD 2,000
        """

        result = self.validator.classify_document_type(bank_statement_text.lower(), DocumentType.INVOICE)

        assert result.result == ValidationResult.SUSPICIOUS_CONTENT
        assert result.confidence > 0.0

    def test_complete_validation_valid_document(self):
        """Test complete document validation for valid document"""
        # Create valid invoice PDF content
        invoice_content = b"%PDF-1.4\nCommercial Invoice\nInvoice No: 12345"

        with patch.object(self.validator, 'extract_text_content') as mock_extract:
            mock_extract.return_value = "commercial invoice\ninvoice no: 12345\ntotal amount: usd 1000"

            result = self.validator.validate_document_type(invoice_content, "invoice.pdf", "invoice")

            assert result.result == ValidationResult.VALID
            assert result.confidence >= 0.3
            assert result.error is None

    def test_complete_validation_invalid_file_type(self):
        """Test complete validation with invalid file type"""
        content = b"some content"

        result = self.validator.validate_document_type(content, "document.docx", "invoice")

        assert result.result == ValidationResult.INVALID_FILE_TYPE
        assert result.error is not None
        assert result.error.error_type == "invalid_file_type"
        assert result.error.file == "document.docx"


class TestAPIEndpoint:
    """Test the enhanced /api/validate endpoint"""

    def setup_method(self):
        """Setup test fixtures"""
        self.client = TestClient(app)

    def test_validate_endpoint_valid_documents(self):
        """Test API endpoint with valid documents"""
        # Create test files
        invoice_content = b"Commercial Invoice\nInvoice No: 12345\nTotal: USD 1000"
        lc_content = b"Letter of Credit\nLC No: LC-001\nUCP 600"

        files = [
            ("files", ("invoice.pdf", io.BytesIO(invoice_content), "application/pdf")),
            ("files", ("lc.pdf", io.BytesIO(lc_content), "application/pdf"))
        ]

        document_tags = json.dumps({
            "invoice.pdf": "invoice",
            "lc.pdf": "lc"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter",
            "workflow_type": "export-lc-upload"
        }

        with patch('document_validator.DocumentValidator.extract_text_content') as mock_extract:
            mock_extract.side_effect = [
                "commercial invoice\ninvoice no: 12345",
                "letter of credit\nlc no: lc-001\nucp 600"
            ]

            response = self.client.post("/api/validate", files=files, data=data)

            # Should succeed and return job info
            assert response.status_code == 200
            result = response.json()
            assert "job_id" in result
            assert result["status"] == "queued"

    def test_validate_endpoint_invalid_file_type(self):
        """Test API endpoint rejects invalid file types"""
        files = [
            ("files", ("document.docx", io.BytesIO(b"invalid content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
        ]

        document_tags = json.dumps({
            "document.docx": "invoice"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter"
        }

        response = self.client.post("/api/validate", files=files, data=data)

        assert response.status_code == 400
        result = response.json()
        assert result["detail"]["error_id"] == "document_validation_failed"
        assert "validation_errors" in result["detail"]
        assert result["detail"]["validation_errors"][0]["error_type"] == "invalid_file_type"

    def test_validate_endpoint_cv_as_invoice(self):
        """Test API endpoint rejects CV uploaded as invoice"""
        cv_content = b"Curriculum Vitae\nJohn Doe\nSoftware Engineer"

        files = [
            ("files", ("cv.pdf", io.BytesIO(cv_content), "application/pdf"))
        ]

        document_tags = json.dumps({
            "cv.pdf": "invoice"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter"
        }

        with patch('document_validator.DocumentValidator.extract_text_content') as mock_extract:
            mock_extract.return_value = "curriculum vitae\njohn doe\nsoftware engineer"

            response = self.client.post("/api/validate", files=files, data=data)

            assert response.status_code == 422  # Invalid document content
            result = response.json()
            assert result["detail"]["error_id"] == "document_validation_failed"
            assert "validation_errors" in result["detail"]

    def test_validate_endpoint_bank_statement_as_invoice(self):
        """Test API endpoint rejects bank statement as invoice"""
        bank_content = b"Bank Statement\nAccount: 123456\nBalance: $10,000"

        files = [
            ("files", ("bank_statement.pdf", io.BytesIO(bank_content), "application/pdf"))
        ]

        document_tags = json.dumps({
            "bank_statement.pdf": "invoice"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter"
        }

        with patch('document_validator.DocumentValidator.extract_text_content') as mock_extract:
            mock_extract.return_value = "bank statement\naccount: 123456\nbalance: $10,000"

            response = self.client.post("/api/validate", files=files, data=data)

            assert response.status_code == 422
            result = response.json()
            assert "validation_errors" in result["detail"]

    def test_validate_endpoint_missing_document_tags(self):
        """Test API endpoint with missing document tags (should default to 'other')"""
        invoice_content = b"Some document content"

        files = [
            ("files", ("document.pdf", io.BytesIO(invoice_content), "application/pdf"))
        ]

        data = {
            "user_type": "exporter"
        }

        response = self.client.post("/api/validate", files=files, data=data)

        # Should succeed because default 'other' type is accepted
        assert response.status_code == 200

    def test_validate_endpoint_malformed_document_tags(self):
        """Test API endpoint with malformed document tags JSON"""
        invoice_content = b"Some document content"

        files = [
            ("files", ("document.pdf", io.BytesIO(invoice_content), "application/pdf"))
        ]

        data = {
            "document_tags": "invalid json",
            "user_type": "exporter"
        }

        response = self.client.post("/api/validate", files=files, data=data)

        # Should succeed with fallback to 'other' type
        assert response.status_code == 200

    def test_validate_endpoint_large_file(self):
        """Test API endpoint rejects files that are too large"""
        # Create content larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)

        files = [
            ("files", ("large_file.pdf", io.BytesIO(large_content), "application/pdf"))
        ]

        document_tags = json.dumps({
            "large_file.pdf": "invoice"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter"
        }

        response = self.client.post("/api/validate", files=files, data=data)

        assert response.status_code == 400
        result = response.json()
        assert "exceeds maximum" in result["detail"]["validation_errors"][0]["error"]

    def test_validate_endpoint_mixed_valid_invalid(self):
        """Test API endpoint with mix of valid and invalid documents"""
        valid_content = b"Commercial Invoice\nInvoice No: 12345"
        invalid_content = b"Curriculum Vitae\nJohn Doe"

        files = [
            ("files", ("valid_invoice.pdf", io.BytesIO(valid_content), "application/pdf")),
            ("files", ("cv.pdf", io.BytesIO(invalid_content), "application/pdf"))
        ]

        document_tags = json.dumps({
            "valid_invoice.pdf": "invoice",
            "cv.pdf": "invoice"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter"
        }

        with patch('document_validator.DocumentValidator.extract_text_content') as mock_extract:
            mock_extract.side_effect = [
                "commercial invoice\ninvoice no: 12345",
                "curriculum vitae\njohn doe"
            ]

            response = self.client.post("/api/validate", files=files, data=data)

            # Should fail because one document is invalid
            assert response.status_code == 422
            result = response.json()
            assert len(result["detail"]["validation_errors"]) == 1  # Only the CV should fail

    def test_cost_protection_no_ocr_llm_call(self):
        """Test that invalid documents don't proceed to OCR/LLM processing"""
        cv_content = b"Curriculum Vitae\nJohn Doe"

        files = [
            ("files", ("cv.pdf", io.BytesIO(cv_content), "application/pdf"))
        ]

        document_tags = json.dumps({
            "cv.pdf": "invoice"
        })

        data = {
            "document_tags": document_tags,
            "user_type": "exporter"
        }

        with patch('document_validator.DocumentValidator.extract_text_content') as mock_extract:
            mock_extract.return_value = "curriculum vitae\njohn doe"

            # Mock any potential OCR/LLM calls that should NOT happen
            with patch('main.some_ocr_service') as mock_ocr, \
                 patch('main.some_llm_service') as mock_llm:

                response = self.client.post("/api/validate", files=files, data=data)

                # Should fail at validation layer
                assert response.status_code == 422

                # OCR/LLM services should NOT be called
                mock_ocr.assert_not_called()
                mock_llm.assert_not_called()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])