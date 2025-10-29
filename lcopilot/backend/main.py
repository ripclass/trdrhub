"""
LCopilot Mock Backend - FastAPI Application
Temporary mock backend for Phase 5 frontend testing

This provides realistic API responses without actual OCR/rules processing.
Replace with real pipeline implementation for production.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    ValidationResponse,
    JobResponse,
    ResultResponse,
    BankProfile,
    User,
    JobStage,
    JobStatus
)
from db import db
from document_validator import DocumentValidator
from validation_metrics import record_validation_metric, get_metrics_collector
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LCopilot Mock API",
    description="Temporary mock backend for LCopilot Phase 5 frontend testing",
    version="1.0.0"
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # LCopilot frontend
        "http://localhost:3001",  # Backup port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Vite default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File size limit (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.json'}


@app.middleware("http")
async def add_request_id_header(request, call_next):
    """Add request ID to all responses for tracing"""
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LCopilot Mock Backend",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_document(
    files: List[UploadFile] = File(...),
    user_type: Optional[str] = Form(None),
    workflow_type: Optional[str] = Form(None),
    lc_number: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    # Document type tags for each file (JSON string mapping filename to type)
    document_tags: Optional[str] = Form(None),
    x_request_id: Optional[str] = Header(None)
):
    """
    Submit documents for validation with enhanced pre-processing validation
    This endpoint accepts multiple file uploads and creates a validation job
    """
    logger.info(f"Validation request: files={[f.filename for f in files]}, user_type={user_type}, workflow={workflow_type}")

    # Parse document tags
    doc_tags = {}
    if document_tags:
        try:
            import json
            doc_tags = json.loads(document_tags)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Invalid document_tags format: {document_tags}")
            # Fallback: assume all documents are 'other' type
            doc_tags = {file.filename: 'other' for file in files}
    else:
        # Default: assume all documents are 'other' type for backward compatibility
        doc_tags = {file.filename: 'other' for file in files}

    # STEP 1: Enhanced Document Validation Layer (before OCR/LLM)
    logger.info("Running enhanced document validation...")
    validation_errors = []
    validation_start_time = time.time()

    try:
        # Create document validator instance
        validator = DocumentValidator()

        for file in files:
            doc_type = doc_tags.get(file.filename, 'other')
            logger.info(f"Validating {file.filename} as {doc_type}")

            # Read file content for validation
            file_content = await file.read()
            file.file.seek(0)  # Reset file pointer for later use

            # Validate document type and content
            validation_result = validator.validate_document_type(
                file_content, file.filename, doc_type
            )

            if validation_result.result.value != 'valid':
                error_detail = {
                    "error": validation_result.error.message,
                    "error_type": validation_result.error.error_type,
                    "file": validation_result.error.file,
                    "expected": validation_result.error.expected,
                    "actual": validation_result.error.actual,
                    "confidence": validation_result.confidence
                }
                validation_errors.append(error_detail)
                logger.warning(f"Document validation failed for {file.filename}: {error_detail}")

    except Exception as e:
        logger.error(f"Document validation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_id": "validation_system_error",
                "type": "internal_error",
                "message": f"Document validation system error: {str(e)}",
                "request_id": x_request_id
            }
        )

    # If any documents failed validation, return errors immediately
    if validation_errors:
        # Record failed validation metrics
        processing_time_ms = (time.time() - validation_start_time) * 1000  # Convert to milliseconds

        record_validation_metric(
            request_id=x_request_id,
            user_type=user_type or 'unknown',
            workflow_type=workflow_type or 'unknown',
            files=files,
            validation_errors=validation_errors,
            validation_passed=False,
            processing_time_ms=processing_time_ms
        )

        # Return 422 for document content validation failures
        status_code = 422 if any(e["error_type"] == "invalid_document_content" for e in validation_errors) else 400

        raise HTTPException(
            status_code=status_code,
            detail={
                "error_id": "document_validation_failed",
                "type": "validation",
                "message": f"Document validation failed for {len(validation_errors)} file(s)",
                "validation_errors": validation_errors,
                "request_id": x_request_id
            }
        )

    logger.info("✅ All documents passed enhanced validation")

    # Record successful validation metrics
    processing_time_ms = (time.time() - validation_start_time) * 1000  # Convert to milliseconds

    record_validation_metric(
        request_id=x_request_id,
        user_type=user_type or 'unknown',
        workflow_type=workflow_type or 'unknown',
        files=files,
        validation_errors=[],  # No errors for successful validation
        validation_passed=True,
        processing_time_ms=processing_time_ms
    )

    # STEP 2: Calculate total size for logging (file validation already done above)
    total_size = sum(file.size or 0 for file in files)

    # Simulate rate limiting for demo (every 7th request)
    import random
    if random.randint(1, 7) == 7:
        raise HTTPException(
            status_code=429,
            detail={
                "error_id": "rate_limit_exceeded",
                "type": "rate_limit",
                "message": "You have exceeded your rate limit. Please upgrade your plan or try again later.",
                "request_id": x_request_id
            }
        )

    # Read file contents (we don't actually process them in mock)
    for file in files:
        content = await file.read()
        logger.info(f"Received file: {file.filename} ({len(content)} bytes)")

    # Create job in mock database
    job_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())

    response = ValidationResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        request_id=request_id,
        created_at=datetime.utcnow().isoformat()
    )

    logger.info(f"Created job: {response.job_id}")
    return response


@app.get("/api/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    x_request_id: Optional[str] = Header(None)
):
    """
    Get job status and progress
    This endpoint simulates job progression through stages
    """
    logger.info(f"Job status request: {job_id}")

    # Simulate job progression - jobs complete after a few seconds
    import time
    import hashlib

    # Use job_id hash to create deterministic but random-seeming behavior
    seed = int(hashlib.md5(job_id.encode()).hexdigest()[:8], 16)
    seconds_elapsed = int(time.time()) % 100  # Simple time-based progression

    if seconds_elapsed < 5:
        status = "processing"
    else:
        status = "completed"

    response = {
        "job_id": job_id,
        "status": status,
        "created_at": datetime.utcnow().isoformat(),
        "user_type": "exporter"  # Could be determined from job data in real implementation
    }

    logger.info(f"Job {job_id}: {status}")
    return response


@app.get("/api/results/{job_id}")
async def get_validation_results(
    job_id: str,
    x_request_id: Optional[str] = Header(None)
):
    """
    Get validation results for a completed job
    Returns findings, score, and evidence download link
    """
    logger.info(f"Results request: {job_id}")

    # Mock validation results
    results = {
        "job_id": job_id,
        "status": "completed",
        "results": {
            "overall_compliance": True,
            "risk_score": 25,
            "issues": [
                {
                    "severity": "medium",
                    "category": "compliance",
                    "description": "Minor discrepancy in beneficiary address format",
                    "recommendation": "Verify beneficiary address format matches LC requirements exactly",
                    "affected_documents": ["Invoice_001.pdf"]
                },
                {
                    "severity": "low",
                    "category": "formatting",
                    "description": "Document date format uses DD/MM/YYYY instead of recommended MM/DD/YYYY",
                    "recommendation": "Consider using MM/DD/YYYY format for international consistency",
                    "affected_documents": ["LC_Draft.pdf"]
                }
            ],
            "documents": [
                {
                    "name": "LC_Draft.pdf",
                    "status": "verified",
                    "issues": []
                },
                {
                    "name": "Invoice_001.pdf",
                    "status": "warning",
                    "issues": ["Address format discrepancy"]
                },
                {
                    "name": "Packing_List.pdf",
                    "status": "verified",
                    "issues": []
                }
            ]
        }
    }

    logger.info(f"Results {job_id}: risk_score={results['results']['risk_score']}")
    return results


@app.get("/api/profiles/banks", response_model=List[BankProfile])
async def get_bank_profiles():
    """
    Get available bank profiles
    Returns list of supported banks with their validation rules
    """
    logger.info("Bank profiles request")
    profiles = db.get_bank_profiles()
    logger.info(f"Returning {len(profiles)} bank profiles")
    return profiles


@app.get("/api/me", response_model=User)
async def get_current_user():
    """
    Get current user information
    Returns mock user with quota information
    """
    logger.info("Current user request")
    user_data = db.get_current_user()
    user = User(
        id=user_data["id"],
        email=user_data["email"],
        organization=user_data["organization"],
        tier=user_data["tier"],
        quota=user_data["quota"],
        usage=user_data["usage"]
    )
    return user


@app.post("/api/pay/sslcommerz/session")
async def create_payment_session(
    amount: int,
    checks: int,
    x_request_id: Optional[str] = Header(None)
):
    """
    Create SSLCommerz payment session (mock)
    Returns redirect URL for payment
    """
    logger.info(f"Payment session: amount={amount}, checks={checks}")

    session_id = str(uuid.uuid4())
    redirect_url = f"http://localhost:3000/billing/callback?session_id={session_id}&status=success&amount={amount}&checks={checks}"

    return {
        "session_id": session_id,
        "redirect_url": redirect_url,
        "amount": amount,
        "currency": "BDT"
    }


@app.get("/api/pay/sslcommerz/callback")
async def payment_callback(
    session_id: Optional[str] = None,
    status: Optional[str] = None,
    amount: Optional[int] = None,
    checks: Optional[int] = None
):
    """
    Handle SSLCommerz payment callback (mock)
    """
    logger.info(f"Payment callback: session_id={session_id}, status={status}")

    if status == "success":
        return {
            "status": "success",
            "transaction_id": f"txn-{str(uuid.uuid4())[:8]}",
            "amount": amount,
            "quota": checks,
            "message": "Payment successful"
        }
    else:
        return {
            "status": "failed",
            "message": "Payment failed or cancelled"
        }


@app.get("/api/dashboard")
async def get_dashboard(user_type: Optional[str] = None):
    """
    Get dashboard statistics for the specified user type
    """
    logger.info(f"Dashboard request for user_type: {user_type}")

    # Mock dashboard stats
    stats = {
        "total_validations": 25,
        "successful_validations": 22,
        "pending_corrections": 3,
        "average_processing_time": "2.3 min",
        "recent_jobs": [
            {
                "job_id": f"job-{uuid.uuid4()}",
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
                "workflow_type": "draft-lc-risk" if user_type == "importer" else None
            },
            {
                "job_id": f"job-{uuid.uuid4()}",
                "status": "processing",
                "created_at": datetime.utcnow().isoformat(),
                "workflow_type": "supplier-document-check" if user_type == "importer" else None
            }
        ]
    }

    return stats


@app.post("/api/amendments")
async def submit_amendment(
    job_id: str = Form(...),
    selected_issues: List[str] = Form(...),
    correction_type: str = Form(...),
    urgency_level: str = Form(...),
    notes: Optional[str] = Form(None)
):
    """
    Submit an amendment request
    """
    logger.info(f"Amendment request for job {job_id}: {len(selected_issues)} issues")

    request_id = f"amend-{uuid.uuid4()}"

    return {"request_id": request_id}


@app.get("/api/evidence/{job_id}/evidence-pack.pdf")
async def download_evidence_pack(job_id: str):
    """
    Download evidence pack (mock)
    Returns a simple text response simulating PDF download
    """
    logger.info(f"Evidence download: {job_id}")

    # In real implementation, this would return the actual PDF file
    return JSONResponse(
        content={"message": f"Mock evidence pack for job {job_id}"},
        headers={"Content-Type": "application/json"}
    )


@app.get("/api/metrics/validation")
async def get_validation_metrics(
    hours: int = 24,
    x_request_id: Optional[str] = Header(None)
):
    """
    Get validation metrics and rejection rates
    Returns comprehensive analytics on document validation performance
    """
    logger.info(f"Validation metrics request for last {hours} hours")

    try:
        collector = get_metrics_collector()

        # Get rejection rates for specified time period
        rejection_data = collector.get_rejection_rates(hours=hours)

        # Get workflow analytics for last 7 days
        workflow_data = collector.get_workflow_analytics(days=7)

        return {
            "rejection_analysis": rejection_data,
            "workflow_analytics": workflow_data,
            "request_id": x_request_id,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to retrieve validation metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_id": "metrics_retrieval_failed",
                "type": "internal_error",
                "message": f"Failed to retrieve validation metrics: {str(e)}",
                "request_id": x_request_id
            }
        )


@app.post("/api/metrics/validation/export")
async def export_validation_metrics(
    hours: int = 168,  # Default to 1 week
    format: str = "csv",
    x_request_id: Optional[str] = Header(None)
):
    """
    Export validation metrics to CSV for analysis
    Returns download information for the exported file
    """
    logger.info(f"Validation metrics export request: {hours} hours, format: {format}")

    try:
        collector = get_metrics_collector()

        if format.lower() == "csv":
            output_file = f"validation_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            result = collector.export_metrics_csv(output_file, hours=hours)

            return {
                "status": "success",
                "message": result,
                "file_path": output_file,
                "format": "csv",
                "period_hours": hours,
                "request_id": x_request_id
            }
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_id": "unsupported_format",
                    "type": "validation",
                    "message": f"Unsupported export format: {format}. Only 'csv' is supported.",
                    "request_id": x_request_id
                }
            )

    except Exception as e:
        logger.error(f"Failed to export validation metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_id": "metrics_export_failed",
                "type": "internal_error",
                "message": f"Failed to export validation metrics: {str(e)}",
                "request_id": x_request_id
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )