"""
Pydantic models for LCopilot Mock Backend
Matches the TypeScript interfaces defined in frontend
"""
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class JobStage(str, Enum):
    QUEUED = "queued"
    OCR = "ocr"
    RULES = "rules"
    EVIDENCE = "evidence"
    DONE = "done"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class BankCategory(str, Enum):
    STATE = "state"
    PRIVATE = "private"
    ISLAMIC = "islamic"
    FOREIGN = "foreign"


class EnforcementLevel(str, Enum):
    STRICT = "strict"
    MEDIUM = "medium"
    FLEXIBLE = "flexible"


class BankProfile(BaseModel):
    code: str
    name: str
    category: BankCategory
    enforcement_level: EnforcementLevel = EnforcementLevel.MEDIUM
    validation_rules: int
    ucp_compliance: bool


class Finding(BaseModel):
    id: str
    category: str
    severity: SeverityLevel
    field: str
    expected: str
    actual: str
    description: str
    ucp_reference: Optional[str] = None


class ValidationResponse(BaseModel):
    job_id: str
    status: JobStatus
    request_id: str
    created_at: datetime


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    stage: JobStage
    progress: int
    request_id: str
    created_at: datetime
    updated_at: datetime
    error: Optional[dict] = None


class ResultResponse(BaseModel):
    job_id: str
    score: int
    findings: List[Finding]
    evidence_url: Optional[str] = None
    evidence_sha256: Optional[str] = None
    correlation_id: str
    request_id: str
    bank_profile: BankProfile
    processing_time: int
    quota: Optional[int] = None
    created_at: datetime


class User(BaseModel):
    id: str
    email: str
    organization: str
    tier: Literal["free", "pro", "enterprise"]
    quota: int
    usage: int