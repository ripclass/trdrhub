"""
Validation session API endpoints.
"""

from datetime import datetime, timezone, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, ValidationSession, SessionStatus
from ..schemas import (
    ValidationSessionCreate, ValidationSessionResponse,
    ValidationSessionDetail, ValidationSessionSummary,
    ReportDownloadResponse, DocumentUploadUrl
)
from ..auth import get_current_user
from ..services import ValidationSessionService, ReportService, S3Service

router = APIRouter(prefix="/sessions", tags=["validation-sessions"])


@router.post("", response_model=ValidationSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_validation_session(
    session_data: ValidationSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new validation session and return pre-signed upload URLs."""
    
    session_service = ValidationSessionService(db)
    s3_service = S3Service()
    
    # Create validation session
    session = session_service.create_session(current_user)
    
    # Generate pre-signed upload URLs for all document types
    upload_urls = s3_service.generate_upload_urls(session.id)
    
    return ValidationSessionResponse(
        session_id=session.id,
        status=session.status,
        upload_urls=upload_urls,
        created_at=session.created_at
    )


@router.get("", response_model=List[ValidationSessionSummary])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all validation sessions for the current user."""
    
    session_service = ValidationSessionService(db)
    sessions = session_service.get_user_sessions(current_user)
    
    # Convert to summary format
    session_summaries = []
    for session in sessions:
        total_documents = len(session.documents)
        total_discrepancies = len(session.discrepancies)
        critical_discrepancies = len([
            d for d in session.discrepancies 
            if d.severity == "critical"
        ])
        
        session_summaries.append(ValidationSessionSummary(
            id=session.id,
            status=session.status,
            created_at=session.created_at,
            total_documents=total_documents,
            total_discrepancies=total_discrepancies,
            critical_discrepancies=critical_discrepancies
        ))
    
    return session_summaries


@router.get("/{session_id}", response_model=ValidationSessionDetail)
async def get_session_detail(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific validation session."""
    
    session_service = ValidationSessionService(db)
    session = session_service.get_session(session_id, current_user)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation session not found"
        )
    
    return ValidationSessionDetail.from_orm(session)


@router.get("/{session_id}/report", response_model=ReportDownloadResponse)
async def get_session_report(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get download URL for the session's validation report."""
    
    session_service = ValidationSessionService(db)
    report_service = ReportService(db)
    
    # Verify session exists and user has access
    session = session_service.get_session(session_id, current_user)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation session not found"
        )
    
    # Check if session is completed
    if session.status != SessionStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation session not completed"
        )
    
    # Get the latest report
    report = report_service.get_latest_report(session)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Generate download URL
    download_url = report_service.generate_download_url(report)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    return ReportDownloadResponse(
        download_url=download_url,
        expires_at=expires_at,
        report_info=report
    )


@router.post("/{session_id}/process")
async def start_session_processing(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start processing a validation session (trigger OCR and validation)."""
    
    session_service = ValidationSessionService(db)
    session = session_service.get_session(session_id, current_user)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation session not found"
        )
    
    # Check if session is in correct state
    if session.status not in [SessionStatus.CREATED.value, SessionStatus.UPLOADING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session cannot be processed in current state"
        )
    
    # Update status to processing
    session = session_service.update_session_status(session, SessionStatus.PROCESSING)
    
    # In stub mode, process documents immediately
    from ..config import settings
    if settings.USE_STUBS:
        # Process documents synchronously in stub mode
        from ..services import DocumentProcessingService
        processing_service = DocumentProcessingService(db)
        
        try:
            await processing_service.process_documents(session)
            session_service.update_session_status(session, SessionStatus.COMPLETED)
        except Exception as e:
            import traceback
            traceback.print_exc()
            session_service.update_session_status(session, SessionStatus.FAILED)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: {str(e)}"
            )
    else:
        # TODO: Queue OCR and validation processing
        # This would typically send a message to SQS to trigger async processing
        pass
    
    return {"message": "Processing started", "session_id": session_id}