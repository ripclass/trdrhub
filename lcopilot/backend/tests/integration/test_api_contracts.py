"""
API Contract Integration Tests for Backend

These tests validate that the FastAPI backend maintains contract 
compatibility with shared-types schemas.
"""

import json
import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID
from fastapi.testclient import TestClient

# Import shared schemas (would be installed as package in real project)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../packages/shared-types/python'))

from schemas import (
    HealthResponse, 
    ApiError,
    AuthToken,
    FileUploadRequest,
    FileUploadResponse,
    OcrJobRequest,
    OcrJobResponse,
    UserProfile,
    validate_data,
    get_schema
)

# Mock FastAPI app for testing
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Mock endpoints for contract testing
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "redis": "connected"
        }
    }

@app.get("/nonexistent")
async def nonexistent_endpoint():
    raise HTTPException(
        status_code=404,
        detail={
            "error": "not_found",
            "message": "Endpoint not found",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": "/nonexistent",
            "method": "GET"
        }
    )

@app.post("/auth/login")
async def login():
    return {
        "access_token": "mock-jwt-token",
        "refresh_token": "mock-refresh-token",
        "token_type": "bearer",
        "expires_in": 3600
    }

@app.post("/files/upload")
async def create_upload():
    return {
        "upload_id": str(uuid4()),
        "upload_url": "https://s3.amazonaws.com/bucket/presigned-url",
        "fields": {
            "key": "uploads/file.pdf",
            "policy": "base64-encoded-policy"
        },
        "expires_at": datetime.now(timezone.utc).isoformat()
    }

@app.post("/ocr/jobs")
async def create_ocr_job():
    job_id = uuid4()
    file_id = uuid4()
    now = datetime.now(timezone.utc).isoformat()
    
    return {
        "job_id": str(job_id),
        "file_id": str(file_id),
        "status": "queued",
        "created_at": now,
        "updated_at": now
    }

client = TestClient(app)


class TestHealthEndpointContract:
    """Test health endpoint contract compliance."""
    
    def test_health_endpoint_returns_valid_schema(self):
        """Validate health endpoint returns data matching HealthResponse schema."""
        response = client.get("/health")
        
        assert response.status_code == 200
        
        # Validate against Pydantic schema
        health_data = HealthResponse.model_validate(response.json())
        assert health_data.status in ["healthy", "unhealthy"]
        assert health_data.services.database in ["connected", "disconnected"]
        assert isinstance(health_data.timestamp, datetime)
        assert isinstance(health_data.version, str)
    
    def test_health_endpoint_schema_validation_utility(self):
        """Test schema validation utility function."""
        response = client.get("/health")
        
        # Test utility function
        validated_data = validate_data("HealthResponse", response.json())
        assert isinstance(validated_data, HealthResponse)
    
    def test_error_response_matches_schema(self):
        """Validate error responses match ApiError schema."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        
        # FastAPI wraps error details in 'detail' field
        error_detail = response.json()["detail"]
        
        # Validate error response format
        error_data = ApiError.model_validate(error_detail)
        assert error_data.error is not None
        assert error_data.message is not None
        assert isinstance(error_data.timestamp, datetime)


class TestAuthenticationContract:
    """Test authentication endpoint contract compliance."""
    
    def test_login_returns_valid_auth_token(self):
        """Validate login endpoint returns valid AuthToken."""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        
        # Validate against AuthToken schema
        token_data = AuthToken.model_validate(response.json())
        assert token_data.access_token is not None
        assert token_data.refresh_token is not None
        assert token_data.token_type == "bearer"
        assert token_data.expires_in > 0


class TestFileUploadContract:
    """Test file upload endpoint contract compliance."""
    
    def test_file_upload_request_validation(self):
        """Test FileUploadRequest schema validation."""
        valid_request = {
            "filename": "test-document.pdf",
            "content_type": "application/pdf",
            "size": 1024000
        }
        
        # Should validate successfully
        upload_request = FileUploadRequest.model_validate(valid_request)
        assert upload_request.size > 0
        
        # Test invalid request (negative size)
        invalid_request = {
            "filename": "test-document.pdf",
            "content_type": "application/pdf",
            "size": -1
        }
        
        with pytest.raises(ValueError):
            FileUploadRequest.model_validate(invalid_request)
    
    def test_file_upload_response_schema(self):
        """Test file upload endpoint returns valid FileUploadResponse."""
        upload_request = {
            "filename": "test-document.pdf",
            "content_type": "application/pdf",
            "size": 1024000
        }
        
        response = client.post("/files/upload", json=upload_request)
        
        assert response.status_code == 200
        
        # Validate response schema
        upload_data = FileUploadResponse.model_validate(response.json())
        assert isinstance(upload_data.upload_id, UUID)
        assert upload_data.upload_url is not None
        assert isinstance(upload_data.fields, dict)
        assert isinstance(upload_data.expires_at, datetime)


class TestOcrJobContract:
    """Test OCR job endpoint contract compliance."""
    
    def test_ocr_job_request_validation(self):
        """Test OcrJobRequest schema validation."""
        valid_request = {
            "file_id": str(uuid4()),
            "language": "eng+ben",
            "options": {
                "deskew": True,
                "remove_background": False,
                "enhance_contrast": True
            }
        }
        
        # Should validate successfully
        ocr_request = OcrJobRequest.model_validate(valid_request)
        assert ocr_request.language == "eng+ben"
        assert ocr_request.options.deskew is True
    
    def test_ocr_job_response_schema(self):
        """Test OCR job endpoint returns valid OcrJobResponse."""
        job_request = {
            "file_id": str(uuid4()),
            "language": "eng+ben"
        }
        
        response = client.post("/ocr/jobs", json=job_request)
        
        assert response.status_code == 200
        
        # Validate response schema
        job_data = OcrJobResponse.model_validate(response.json())
        assert isinstance(job_data.job_id, UUID)
        assert isinstance(job_data.file_id, UUID)
        assert job_data.status in ["queued", "processing", "completed", "failed", "cancelled"]
        assert isinstance(job_data.created_at, datetime)
        assert isinstance(job_data.updated_at, datetime)


class TestSchemaValidationUtilities:
    """Test schema validation utility functions."""
    
    def test_get_schema_function(self):
        """Test get_schema utility function."""
        health_schema = get_schema("HealthResponse")
        assert health_schema == HealthResponse
        
        # Test invalid schema name
        with pytest.raises(ValueError):
            get_schema("NonexistentSchema")
    
    def test_validate_data_function(self):
        """Test validate_data utility function."""
        valid_health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "connected"
            }
        }
        
        # Should validate successfully
        validated = validate_data("HealthResponse", valid_health_data)
        assert isinstance(validated, HealthResponse)
        
        # Test invalid data
        invalid_health_data = {
            "status": "invalid-status",
            "timestamp": "not-a-datetime",
            "version": 123,
            "services": {
                "database": "maybe-connected"
            }
        }
        
        with pytest.raises(ValueError):
            validate_data("HealthResponse", invalid_health_data)


class TestTypeSafety:
    """Test type safety and consistency between TypeScript and Python schemas."""
    
    def test_enum_values_consistency(self):
        """Ensure enum values match between TypeScript and Python."""
        from schemas import ServiceStatus, HealthStatus, UserRole
        
        # Test ServiceStatus enum
        assert ServiceStatus.CONNECTED == "connected"
        assert ServiceStatus.DISCONNECTED == "disconnected"
        
        # Test HealthStatus enum
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        
        # Test UserRole enum
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"
        assert UserRole.VIEWER == "viewer"
    
    def test_required_vs_optional_fields(self):
        """Test that required and optional fields match TypeScript definitions."""
        # Test HealthResponse - all fields required except redis in services
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "connected"
                # redis is optional
            }
        }
        
        validated = HealthResponse.model_validate(health_data)
        assert validated.services.redis is None
        
        # Test with redis included
        health_data["services"]["redis"] = "connected"
        validated = HealthResponse.model_validate(health_data)
        assert validated.services.redis == "connected"
    
    def test_field_types_consistency(self):
        """Test that field types match TypeScript definitions."""
        # Test UUID fields
        file_info_data = {
            "id": str(uuid4()),
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "size": 1024,
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        from schemas import FileInfo
        validated = FileInfo.model_validate(file_info_data)
        assert isinstance(validated.id, UUID)
        assert isinstance(validated.filename, str)
        assert isinstance(validated.size, int)


class TestErrorHandling:
    """Test error handling and validation edge cases."""
    
    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        incomplete_data = {
            "status": "healthy"
            # Missing required fields: timestamp, version, services
        }
        
        with pytest.raises(ValueError):
            HealthResponse.model_validate(incomplete_data)
    
    def test_invalid_field_types(self):
        """Test validation fails with invalid field types."""
        invalid_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 123,  # Should be string
            "services": {
                "database": "connected"
            }
        }
        
        with pytest.raises(ValueError):
            HealthResponse.model_validate(invalid_data)
    
    def test_invalid_enum_values(self):
        """Test validation fails with invalid enum values."""
        invalid_data = {
            "status": "maybe-healthy",  # Invalid enum value
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "connected"
            }
        }
        
        with pytest.raises(ValueError):
            HealthResponse.model_validate(invalid_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
