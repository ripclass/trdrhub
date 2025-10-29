"""
Tests for the document processing endpoint.
"""

import pytest
import json
from io import BytesIO
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import User, ValidationSession, Document
from app.auth import get_current_user
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_process_document.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user():
    """Override auth dependency for testing."""
    return User(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def create_test_pdf_content():
    """Create a simple PDF-like content for testing."""
    # This is a minimal PDF header - in real tests you'd use a proper PDF
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n%%EOF"


def create_test_file(filename: str, content_type: str = "application/pdf"):
    """Create a test file for upload."""
    content = create_test_pdf_content()
    return ("files", (filename, BytesIO(content), content_type))


class TestProcessDocument:
    """Test cases for document processing endpoint."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Clear test database
        db = TestingSessionLocal()
        db.query(Document).delete()
        db.query(ValidationSession).delete()
        db.commit()
        db.close()

    @patch('app.services.S3Service.upload_file')
    @patch('app.services.DocumentAIService.process_file')
    def test_process_single_document_success(self, mock_docai, mock_s3):
        """Test successful processing of a single document."""
        # Mock S3 upload
        mock_s3.return_value = {
            's3_key': 'uploads/test-session/letter_of_credit/test.pdf',
            's3_url': 'https://bucket.s3.region.amazonaws.com/uploads/test-session/letter_of_credit/test.pdf',
            'file_size': 1024,
            'content_type': 'application/pdf',
            'original_filename': 'test_lc.pdf'
        }

        # Mock Document AI processing
        mock_docai.return_value = {
            'success': True,
            'extracted_text': 'This is extracted text from the document containing important information.',
            'extracted_fields': {
                'amount': {'value': '$100,000', 'confidence': 0.95},
                'beneficiary': {'value': 'Test Company', 'confidence': 0.88}
            },
            'overall_confidence': 0.91,
            'page_count': 1,
            'processor_id': '42d3342d260e1bf2',
            'processor_version': 'v1.0',
            'entity_count': 2
        }

        # Create test file
        files = [create_test_file("test_lc.pdf")]

        # Make request
        response = client.post("/documents/process-document", files=files)

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert 'session_id' in data
        assert data['processor_id'] == '42d3342d260e1bf2'
        assert len(data['processed_documents']) == 1

        doc = data['processed_documents'][0]
        assert doc['document_type'] == 'letter_of_credit'
        assert doc['original_filename'] == 'test_lc.pdf'
        assert doc['file_size'] == 1024
        assert doc['ocr_confidence'] == 0.91
        assert doc['page_count'] == 1
        assert doc['entity_count'] == 2
        assert 'amount' in doc['extracted_fields']
        assert doc['extracted_text_preview'] == 'This is extracted text from the document containing important information.'

        # Verify S3 and DocAI were called
        mock_s3.assert_called_once()
        mock_docai.assert_called_once()

    @patch('app.services.S3Service.upload_file')
    @patch('app.services.DocumentAIService.process_file')
    def test_process_multiple_documents_success(self, mock_docai, mock_s3):
        """Test successful processing of multiple documents."""
        # Mock S3 upload (called for each file)
        mock_s3.side_effect = [
            {
                's3_key': 'uploads/test-session/letter_of_credit/lc.pdf',
                's3_url': 'https://bucket.s3.region.amazonaws.com/uploads/test-session/letter_of_credit/lc.pdf',
                'file_size': 1024,
                'content_type': 'application/pdf',
                'original_filename': 'lc.pdf'
            },
            {
                's3_key': 'uploads/test-session/commercial_invoice/invoice.pdf',
                's3_url': 'https://bucket.s3.region.amazonaws.com/uploads/test-session/commercial_invoice/invoice.pdf',
                'file_size': 2048,
                'content_type': 'application/pdf',
                'original_filename': 'invoice.pdf'
            }
        ]

        # Mock Document AI processing (called for each file)
        mock_docai.side_effect = [
            {
                'success': True,
                'extracted_text': 'Letter of Credit text content',
                'extracted_fields': {'amount': {'value': '$100,000', 'confidence': 0.95}},
                'overall_confidence': 0.91,
                'page_count': 1,
                'entity_count': 1
            },
            {
                'success': True,
                'extracted_text': 'Commercial Invoice text content',
                'extracted_fields': {'invoice_amount': {'value': '$99,500', 'confidence': 0.93}},
                'overall_confidence': 0.89,
                'page_count': 2,
                'entity_count': 1
            }
        ]

        # Create test files
        files = [
            create_test_file("lc.pdf"),
            create_test_file("invoice.pdf")
        ]

        # Make request
        response = client.post("/documents/process-document", files=files)

        # Assertions
        assert response.status_code == 200
        data = response.json()

        assert len(data['processed_documents']) == 2
        assert data['processing_summary']['total_files_processed'] == 2
        assert data['processing_summary']['average_confidence'] == 0.9  # (0.91 + 0.89) / 2

        # Check document types are correctly assigned
        doc_types = [doc['document_type'] for doc in data['processed_documents']]
        assert 'letter_of_credit' in doc_types
        assert 'commercial_invoice' in doc_types

    def test_process_document_no_files(self):
        """Test error when no files are provided."""
        response = client.post("/documents/process-document", files=[])

        assert response.status_code == 422  # FastAPI validation error

    def test_process_document_too_many_files(self):
        """Test error when more than 3 files are provided."""
        files = [
            create_test_file("file1.pdf"),
            create_test_file("file2.pdf"),
            create_test_file("file3.pdf"),
            create_test_file("file4.pdf")  # Too many
        ]

        response = client.post("/documents/process-document", files=files)

        assert response.status_code == 400
        assert "Maximum 3 files allowed" in response.json()['detail']

    def test_process_document_invalid_file_type(self):
        """Test error when unsupported file type is provided."""
        files = [("files", ("test.txt", BytesIO(b"text content"), "text/plain"))]

        response = client.post("/documents/process-document", files=files)

        assert response.status_code == 400
        assert "not supported" in response.json()['detail']

    @patch('app.services.S3Service.upload_file')
    def test_process_document_s3_failure(self, mock_s3):
        """Test handling of S3 upload failure."""
        # Mock S3 upload failure
        mock_s3.side_effect = Exception("S3 upload failed")

        files = [create_test_file("test.pdf")]

        response = client.post("/documents/process-document", files=files)

        assert response.status_code == 500
        assert "Failed to process test.pdf" in response.json()['detail']

    @patch('app.services.S3Service.upload_file')
    @patch('app.services.DocumentAIService.process_file')
    def test_process_document_docai_failure(self, mock_docai, mock_s3):
        """Test handling of Document AI processing failure."""
        # Mock successful S3 upload
        mock_s3.return_value = {
            's3_key': 'uploads/test-session/letter_of_credit/test.pdf',
            's3_url': 'https://bucket.s3.region.amazonaws.com/test.pdf',
            'file_size': 1024,
            'content_type': 'application/pdf',
            'original_filename': 'test.pdf'
        }

        # Mock Document AI failure
        mock_docai.return_value = {
            'success': False,
            'error': 'Permission denied',
            'error_type': 'permission_denied'
        }

        files = [create_test_file("test.pdf")]

        response = client.post("/documents/process-document", files=files)

        assert response.status_code == 500
        assert "Document AI processing failed" in response.json()['detail']

    @patch('app.services.S3Service.upload_file')
    @patch('app.services.DocumentAIService.process_file')
    def test_process_document_with_existing_session(self, mock_docai, mock_s3):
        """Test processing documents with an existing session ID."""
        # First create a session by making a request without session_id
        mock_s3.return_value = {
            's3_key': 'uploads/test-session/letter_of_credit/test.pdf',
            's3_url': 'https://bucket.s3.region.amazonaws.com/test.pdf',
            'file_size': 1024,
            'content_type': 'application/pdf',
            'original_filename': 'test.pdf'
        }

        mock_docai.return_value = {
            'success': True,
            'extracted_text': 'Test content',
            'extracted_fields': {},
            'overall_confidence': 0.9,
            'page_count': 1,
            'entity_count': 0
        }

        # First request creates a new session
        files = [create_test_file("test1.pdf")]
        response1 = client.post("/documents/process-document", files=files)
        assert response1.status_code == 200

        session_id = response1.json()['session_id']

        # Second request uses existing session
        files = [create_test_file("test2.pdf")]
        data = {"session_id": session_id}
        response2 = client.post("/documents/process-document", files=files, data=data)

        assert response2.status_code == 200
        assert response2.json()['session_id'] == session_id

    def test_document_type_determination(self):
        """Test document type determination logic."""
        from app.routers.documents import _determine_document_type

        # Test filename-based detection
        assert _determine_document_type("letter_of_credit.pdf", 0) == "letter_of_credit"
        assert _determine_document_type("commercial_invoice.pdf", 0) == "commercial_invoice"
        assert _determine_document_type("bill_of_lading.pdf", 0) == "bill_of_lading"

        # Test partial matches
        assert _determine_document_type("lc_document.pdf", 0) == "letter_of_credit"
        assert _determine_document_type("invoice_123.pdf", 0) == "commercial_invoice"
        assert _determine_document_type("bl_shipping.pdf", 0) == "bill_of_lading"

        # Test position-based fallback
        assert _determine_document_type("unknown.pdf", 0) == "letter_of_credit"
        assert _determine_document_type("unknown.pdf", 1) == "commercial_invoice"
        assert _determine_document_type("unknown.pdf", 2) == "bill_of_lading"
        assert _determine_document_type("unknown.pdf", 5) == "letter_of_credit"  # fallback

    @patch('app.services.DocumentAIService.__init__')
    def test_docai_service_initialization_failure(self, mock_init):
        """Test handling of Document AI service initialization failure."""
        mock_init.side_effect = ValueError("Google Document AI configuration incomplete")

        files = [create_test_file("test.pdf")]

        response = client.post("/documents/process-document", files=files)

        assert response.status_code == 500

    def teardown_method(self):
        """Clean up after each test."""
        # Clear test database
        db = TestingSessionLocal()
        db.query(Document).delete()
        db.query(ValidationSession).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])