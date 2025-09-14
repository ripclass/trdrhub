"""
Business logic services for LCopilot.
"""

import os
import boto3
import tempfile
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from fastapi import UploadFile

from .models import (
    ValidationSession, Document, DocumentType, SessionStatus,
    Discrepancy, Report, User
)
from .schemas import DocumentUploadUrl
from .rules.engine import RulesEngine
from .reports.generator import ReportGenerator
from .ocr.factory import get_ocr_factory
from .config import settings


class S3Service:
    """Service for S3 operations with stub support."""
    
    def __init__(self):
        # Use stub storage if configured
        if settings.USE_STUBS:
            from .stubs.storage_stub import StubS3Service
            self._impl = StubS3Service()
            print("Using stub S3 service for local development")
        else:
            # Real S3 implementation
            self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
            self.bucket_name = settings.S3_BUCKET_NAME
            self.region = settings.AWS_REGION
            print(f"Using real S3 service (bucket: {self.bucket_name})")
    
    def generate_upload_urls(self, session_id: UUID) -> List[DocumentUploadUrl]:
        """Generate pre-signed URLs for document uploads."""
        if settings.USE_STUBS:
            return self._impl.generate_upload_urls(session_id)
        else:
            return self._generate_real_upload_urls(session_id)
    
    def _generate_real_upload_urls(self, session_id: UUID) -> List[DocumentUploadUrl]:
        """Generate real AWS S3 pre-signed URLs for document uploads."""
        upload_urls = []
        
        # Generate URLs for all three document types
        document_types = [
            DocumentType.LETTER_OF_CREDIT,
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.BILL_OF_LADING
        ]
        
        for doc_type in document_types:
            key = f"uploads/{session_id}/{doc_type.value}/{uuid4()}"
            
            try:
                presigned_url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': key,
                        'ContentType': 'application/pdf'  # Default, can be overridden
                    },
                    ExpiresIn=3600  # 1 hour
                )
                
                upload_urls.append(DocumentUploadUrl(
                    document_type=doc_type,
                    upload_url=presigned_url,
                    s3_key=key
                ))
                
            except ClientError as e:
                print(f"Error generating presigned URL: {e}")
                continue
        
        return upload_urls
    
    def generate_download_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate pre-signed URL for downloading a file."""
        if settings.USE_STUBS:
            return self._impl.generate_download_url(s3_key, expires_in)
        else:
            return self._generate_real_download_url(s3_key, expires_in)

    def _generate_real_download_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate real AWS S3 pre-signed URL for downloading a file."""
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
        except ClientError as e:
            print(f"Error generating download URL: {e}")
            raise

    async def upload_file(self, file: UploadFile, session_id: UUID, document_type: str) -> Dict[str, Any]:
        """Upload a file directly to S3 and return metadata."""
        if settings.USE_STUBS:
            return await self._impl.upload_file(file, session_id, document_type)
        else:
            return await self._upload_real_file(file, session_id, document_type)

    async def _upload_real_file(self, file: UploadFile, session_id: UUID, document_type: str) -> Dict[str, Any]:
        """Upload file directly to real S3."""
        try:
            # Generate S3 key
            file_extension = os.path.splitext(file.filename or "")[1]
            s3_key = f"uploads/{session_id}/{document_type}/{uuid4()}{file_extension}"

            # Read file content
            file_content = await file.read()
            file_size = len(file_content)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type or 'application/octet-stream',
                Metadata={
                    'original_filename': file.filename or 'unknown',
                    'session_id': str(session_id),
                    'document_type': document_type,
                    'uploaded_at': datetime.now(timezone.utc).isoformat()
                }
            )

            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

            return {
                's3_key': s3_key,
                's3_url': s3_url,
                'file_size': file_size,
                'content_type': file.content_type or 'application/octet-stream',
                'original_filename': file.filename or 'unknown'
            }

        except ClientError as e:
            logging.error(f"Error uploading file to S3: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error uploading file: {e}")
            raise


class ValidationSessionService:
    """Service for managing validation sessions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_service = S3Service()
    
    def create_session(self, user: User) -> ValidationSession:
        """Create a new validation session."""
        session = ValidationSession(
            user_id=user.id,
            status=SessionStatus.CREATED
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_user_sessions(self, user: User) -> List[ValidationSession]:
        """Get all validation sessions for a user."""
        return self.db.query(ValidationSession).filter(
            ValidationSession.user_id == user.id,
            ValidationSession.deleted_at.is_(None)
        ).order_by(ValidationSession.created_at.desc()).all()
    
    def get_session(self, session_id: UUID, user: User) -> Optional[ValidationSession]:
        """Get a specific validation session."""
        return self.db.query(ValidationSession).filter(
            ValidationSession.id == session_id,
            ValidationSession.user_id == user.id,
            ValidationSession.deleted_at.is_(None)
        ).first()
    
    def update_session_status(self, session: ValidationSession, status: SessionStatus) -> ValidationSession:
        """Update validation session status."""
        session.status = status.value
        session.updated_at = datetime.now(timezone.utc)
        
        if status == SessionStatus.PROCESSING:
            session.processing_started_at = datetime.now(timezone.utc)
        elif status == SessionStatus.COMPLETED:
            session.processing_completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(session)
        return session


class DocumentProcessingService:
    """Service for document processing and OCR."""
    
    def __init__(self, db: Session):
        self.db = db
        self.ocr_factory = get_ocr_factory()
        self.rules_engine = RulesEngine(db)
    
    def create_document_record(
        self,
        session: ValidationSession,
        document_type: DocumentType,
        original_filename: str,
        s3_key: str,
        file_size: int,
        content_type: str
    ) -> Document:
        """Create a document record in the database."""
        document = Document(
            validation_session_id=session.id,
            document_type=document_type.value,
            original_filename=original_filename,
            s3_key=s3_key,
            file_size=file_size,
            content_type=content_type
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    async def process_documents(self, session: ValidationSession):
        """Process all documents in a validation session."""
        try:
            # Get OCR adapter
            ocr_adapter = await self.ocr_factory.get_adapter()
            
            # Get all documents for this session
            documents = self.db.query(Document).filter(
                Document.validation_session_id == session.id,
                Document.deleted_at.is_(None)
            ).all()
            
            # Process each document with OCR
            ocr_results = []
            for document in documents:
                ocr_result = await ocr_adapter.process_document(
                    s3_bucket=os.getenv('S3_BUCKET_NAME', 'lcopilot-documents'),
                    s3_key=document.s3_key,
                    document_id=document.id
                )
                ocr_results.append(ocr_result)
            
            # Update documents with OCR results
            await self.rules_engine.process_ocr_results(session, ocr_results)
            
            # Run validation rules
            validation_summary = await self.rules_engine.validate_session(session)
            
            # Update session with validation results
            session.validation_results = {
                "summary": {
                    "total_rules": validation_summary.total_rules,
                    "passed_rules": validation_summary.passed_rules,
                    "failed_rules": validation_summary.failed_rules,
                    "critical_issues": validation_summary.critical_issues
                },
                "validated_at": validation_summary.validated_at.isoformat()
            }
            
            self.db.commit()
            
            return validation_summary
            
        except Exception as e:
            print(f"Error processing documents: {e}")
            # Update session status to failed
            session.status = SessionStatus.FAILED.value
            self.db.commit()
            raise


class ReportService:
    """Service for generating and managing reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_service = S3Service()
        self.report_generator = ReportGenerator()
    
    def get_latest_report(self, session: ValidationSession) -> Optional[Report]:
        """Get the latest report for a session."""
        return self.db.query(Report).filter(
            Report.validation_session_id == session.id,
            Report.deleted_at.is_(None)
        ).order_by(Report.report_version.desc()).first()
    
    async def generate_report(
        self, 
        session: ValidationSession,
        user: User,
        language: str = "en"
    ) -> Report:
        """Generate a new PDF report for a validation session."""
        # Get validation summary from the rules engine
        rules_engine = RulesEngine(self.db)
        validation_summary = await rules_engine.validate_session(session)
        
        # Generate the report
        report = await self.report_generator.generate_report(
            summary=validation_summary,
            session=session,
            user=user,
            language=language
        )
        
        # Save to database
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def generate_download_url(self, report: Report) -> str:
        """Generate download URL for a report."""
        return self.s3_service.generate_download_url(report.s3_key)


class DocumentAIService:
    """Service for Document AI processing with direct file handling."""

    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_DOCUMENTAI_LOCATION or "eu"
        self.processor_id = settings.GOOGLE_DOCUMENTAI_PROCESSOR_ID

        if not all([self.project_id, self.processor_id]):
            raise ValueError("Google Document AI configuration incomplete")

        # Initialize Document AI client
        try:
            from google.cloud import documentai
            from google.api_core import exceptions as gcp_exceptions

            # Configure client for regional endpoint
            if self.location and self.location != 'us':
                client_options = {"api_endpoint": f"{self.location}-documentai.googleapis.com"}
                self.client = documentai.DocumentProcessorServiceClient(client_options=client_options)
            else:
                self.client = documentai.DocumentProcessorServiceClient()

            self.processor_name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
            self.gcp_exceptions = gcp_exceptions

        except ImportError:
            raise ImportError("google-cloud-documentai package not installed")

    async def process_file(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Process a file directly with Document AI."""
        try:
            from google.cloud import documentai

            # Create Document AI request
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )

            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )

            # Process the document
            result = self.client.process_document(request=request)
            document = result.document

            # Extract structured data
            extracted_text = document.text
            extracted_fields = {}

            # Process entities (form fields)
            if document.entities:
                for entity in document.entities:
                    field_name = entity.type_
                    field_value = entity.mention_text
                    confidence = getattr(entity, 'confidence', 0.0)

                    extracted_fields[field_name] = {
                        'value': field_value,
                        'confidence': confidence
                    }

            # Calculate overall confidence
            confidence_scores = [entity.confidence for entity in document.entities if hasattr(entity, 'confidence') and entity.confidence > 0]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

            return {
                'success': True,
                'extracted_text': extracted_text,
                'extracted_fields': extracted_fields,
                'overall_confidence': overall_confidence,
                'page_count': len(document.pages) if document.pages else 0,
                'processor_id': self.processor_id,
                'processor_version': getattr(result, 'processor_version', 'unknown'),
                'entity_count': len(document.entities) if document.entities else 0
            }

        except self.gcp_exceptions.InvalidArgument as e:
            logging.error(f"Invalid document or request: {e}")
            return {
                'success': False,
                'error': f"Invalid document format: {str(e)}",
                'error_type': 'invalid_document'
            }
        except self.gcp_exceptions.PermissionDenied as e:
            logging.error(f"Permission denied: {e}")
            return {
                'success': False,
                'error': f"Permission denied: {str(e)}",
                'error_type': 'permission_denied'
            }
        except self.gcp_exceptions.NotFound as e:
            logging.error(f"Processor not found: {e}")
            return {
                'success': False,
                'error': f"Document AI processor not found: {str(e)}",
                'error_type': 'processor_not_found'
            }
        except Exception as e:
            logging.error(f"Unexpected error in Document AI: {e}")
            return {
                'success': False,
                'error': f"Document processing failed: {str(e)}",
                'error_type': 'processing_error'
            }