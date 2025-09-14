"""
Document processing API endpoints.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, ValidationSession, Document, DocumentType, SessionStatus
from ..schemas import DocumentProcessingResponse, ProcessedDocumentInfo
from ..auth import get_current_user
from ..services import (
    ValidationSessionService, S3Service, DocumentAIService,
    DocumentProcessingService
)
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["document-processing"])


@router.post("/process-document", response_model=DocumentProcessingResponse, status_code=status.HTTP_200_OK)
async def process_document(
    files: List[UploadFile] = File(..., description="1-3 PDF files (LC, Invoice, BL)"),
    session_id: Optional[str] = Form(None, description="Optional existing session ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process document uploads end-to-end:
    1. Upload files to S3
    2. Process with Google Cloud Document AI
    3. Save results to Postgres
    4. Return structured JSON response
    """
    logger.info(f"Processing {len(files)} documents for user {current_user.id}")

    # Validate file count
    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file must be provided"
        )

    if len(files) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 files allowed"
        )

    # Validate file types
    allowed_types = {'application/pdf', 'image/jpeg', 'image/png', 'image/tiff'}
    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not supported. Use PDF, JPEG, PNG, or TIFF."
            )

    # Initialize services
    session_service = ValidationSessionService(db)
    s3_service = S3Service()
    docai_service = DocumentAIService()

    try:
        # Create or get validation session
        if session_id:
            try:
                session_uuid = UUID(session_id)
                session = session_service.get_session(session_uuid, current_user)
                if not session:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Session not found"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid session ID format"
                )
        else:
            # Create new session
            session = session_service.create_session(current_user)
            logger.info(f"Created new session: {session.id}")

        # Update session status to processing
        session = session_service.update_session_status(session, SessionStatus.PROCESSING)
        session.ocr_provider = "google_documentai"
        db.commit()

        processed_documents = []
        total_confidence = 0.0
        total_entities = 0
        total_pages = 0

        # Process each file
        for idx, file in enumerate(files):
            logger.info(f"Processing file {idx + 1}/{len(files)}: {file.filename}")

            # Determine document type based on filename or order
            document_type = _determine_document_type(file.filename, idx)

            try:
                # Step 1: Upload to S3
                logger.info(f"Uploading {file.filename} to S3...")
                upload_result = await s3_service.upload_file(file, session.id, document_type)

                # Step 2: Process with Document AI
                logger.info(f"Processing {file.filename} with Document AI...")

                # Reset file pointer for processing
                await file.seek(0)
                file_content = await file.read()

                docai_result = await docai_service.process_file(
                    file_content,
                    file.content_type or 'application/pdf'
                )

                if not docai_result['success']:
                    logger.error(f"Document AI processing failed: {docai_result.get('error', 'Unknown error')}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Document AI processing failed: {docai_result.get('error', 'Unknown error')}"
                    )

                # Step 3: Save to database
                logger.info(f"Saving document metadata to database...")
                document = Document(
                    validation_session_id=session.id,
                    document_type=document_type,
                    original_filename=upload_result['original_filename'],
                    s3_key=upload_result['s3_key'],
                    file_size=upload_result['file_size'],
                    content_type=upload_result['content_type'],
                    ocr_text=docai_result['extracted_text'],
                    ocr_confidence=docai_result['overall_confidence'],
                    ocr_processed_at=datetime.now(timezone.utc),
                    extracted_fields=docai_result['extracted_fields']
                )

                db.add(document)
                db.commit()
                db.refresh(document)

                # Prepare response data
                text_preview = docai_result['extracted_text'][:200] if docai_result['extracted_text'] else ""

                processed_doc_info = ProcessedDocumentInfo(
                    document_id=document.id,
                    document_type=document_type,
                    original_filename=upload_result['original_filename'],
                    s3_url=upload_result['s3_url'],
                    s3_key=upload_result['s3_key'],
                    file_size=upload_result['file_size'],
                    extracted_text_preview=text_preview,
                    extracted_fields=docai_result['extracted_fields'],
                    ocr_confidence=docai_result['overall_confidence'],
                    page_count=docai_result['page_count'],
                    entity_count=docai_result['entity_count']
                )

                processed_documents.append(processed_doc_info)

                # Accumulate stats
                total_confidence += docai_result['overall_confidence']
                total_entities += docai_result['entity_count']
                total_pages += docai_result['page_count']

                logger.info(f"Successfully processed {file.filename}")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to process {file.filename}: {str(e)}"
                )

        # Update session status to completed
        session = session_service.update_session_status(session, SessionStatus.COMPLETED)

        # Calculate processing summary
        avg_confidence = total_confidence / len(files) if len(files) > 0 else 0.0
        processing_summary = {
            'total_files_processed': len(files),
            'average_confidence': round(avg_confidence, 3),
            'total_entities_extracted': total_entities,
            'total_pages_processed': total_pages,
            'processor_used': docai_service.processor_id,
            'processing_completed_at': datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Successfully processed all documents for session {session.id}")

        # Return response
        return DocumentProcessingResponse(
            session_id=session.id,
            processor_id=docai_service.processor_id,
            processed_documents=processed_documents,
            discrepancies=[],  # Placeholder - would be populated by validation rules
            processing_summary=processing_summary,
            created_at=session.created_at
        )

    except HTTPException:
        # Update session status to failed for HTTP errors
        try:
            session_service.update_session_status(session, SessionStatus.FAILED)
        except:
            pass
        raise
    except Exception as e:
        # Update session status to failed for unexpected errors
        try:
            session_service.update_session_status(session, SessionStatus.FAILED)
        except:
            pass

        logger.error(f"Unexpected error in document processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


def _determine_document_type(filename: Optional[str], index: int) -> str:
    """Determine document type based on filename or position."""
    if not filename:
        # Fallback to position-based mapping
        type_mapping = {
            0: DocumentType.LETTER_OF_CREDIT.value,
            1: DocumentType.COMMERCIAL_INVOICE.value,
            2: DocumentType.BILL_OF_LADING.value
        }
        return type_mapping.get(index, DocumentType.LETTER_OF_CREDIT.value)

    filename_lower = filename.lower()

    # Check for common patterns in filename
    if any(pattern in filename_lower for pattern in ['lc', 'letter', 'credit']):
        return DocumentType.LETTER_OF_CREDIT.value
    elif any(pattern in filename_lower for pattern in ['invoice', 'inv']):
        return DocumentType.COMMERCIAL_INVOICE.value
    elif any(pattern in filename_lower for pattern in ['bl', 'bill', 'lading', 'shipping']):
        return DocumentType.BILL_OF_LADING.value
    else:
        # Default mapping based on order
        return _determine_document_type(None, index)