"""
In-memory mock database for LCopilot backend
This will be replaced with real database in production
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from models import JobStage, JobStatus, Finding, BankProfile, ResultResponse, SeverityLevel, BankCategory, EnforcementLevel


class MockDatabase:
    def __init__(self):
        # In-memory storage for jobs
        self.jobs: Dict[str, dict] = {}
        self.results: Dict[str, ResultResponse] = {}
        self.bank_profiles = self._create_bank_profiles()
        self.mock_user = {
            "id": "user-123",
            "email": "test@company.bd",
            "organization": "Test Export Ltd",
            "tier": "free",
            "quota": 5,
            "usage": 2
        }

    def _create_bank_profiles(self) -> List[BankProfile]:
        """Create mock bank profiles matching real Bangladesh banks"""
        return [
            BankProfile(
                code="sonali",
                name="Sonali Bank Limited",
                category=BankCategory.STATE,
                enforcement_level=EnforcementLevel.STRICT,
                validation_rules=147,
                ucp_compliance=True
            ),
            BankProfile(
                code="dbbl",
                name="Dutch-Bangla Bank Limited",
                category=BankCategory.PRIVATE,
                enforcement_level=EnforcementLevel.MEDIUM,
                validation_rules=134,
                ucp_compliance=True
            ),
            BankProfile(
                code="hsbc_bd",
                name="HSBC Bangladesh",
                category=BankCategory.FOREIGN,
                enforcement_level=EnforcementLevel.FLEXIBLE,
                validation_rules=152,
                ucp_compliance=True
            ),
            BankProfile(
                code="islami",
                name="Islami Bank Bangladesh Limited",
                category=BankCategory.ISLAMIC,
                enforcement_level=EnforcementLevel.STRICT,
                validation_rules=161,
                ucp_compliance=True
            )
        ]

    def create_job(self, file_name: str, bank_code: str, async_mode: bool) -> dict:
        """Create a new validation job"""
        job_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        now = datetime.utcnow()

        job_data = {
            "job_id": job_id,
            "request_id": request_id,
            "file_name": file_name,
            "bank_code": bank_code,
            "async_mode": async_mode,
            "status": JobStatus.QUEUED,
            "stage": JobStage.QUEUED,
            "progress": 0,
            "created_at": now,
            "updated_at": now,
            "poll_count": 0,  # Track how many times this job was polled
            "error": None
        }

        self.jobs[job_id] = job_data

        # Create mock results immediately (they'll be revealed when job completes)
        self._create_mock_results(job_id, request_id, bank_code)

        return {
            "job_id": job_id,
            "status": JobStatus.QUEUED,
            "request_id": request_id,
            "created_at": now
        }

    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job status and simulate progress"""
        if job_id not in self.jobs:
            return None

        job = self.jobs[job_id]
        job["poll_count"] += 1

        # Simulate job progression based on poll count
        if job["poll_count"] <= 2:
            job["stage"] = JobStage.QUEUED
            job["progress"] = 5
            job["status"] = JobStatus.QUEUED
        elif job["poll_count"] <= 4:
            job["stage"] = JobStage.OCR
            job["progress"] = 25
            job["status"] = JobStatus.PROCESSING
        elif job["poll_count"] <= 6:
            job["stage"] = JobStage.RULES
            job["progress"] = 60
            job["status"] = JobStatus.PROCESSING
        elif job["poll_count"] <= 8:
            job["stage"] = JobStage.EVIDENCE
            job["progress"] = 85
            job["status"] = JobStatus.PROCESSING
        else:
            job["stage"] = JobStage.DONE
            job["progress"] = 100
            job["status"] = JobStatus.COMPLETED

        job["updated_at"] = datetime.utcnow()

        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "stage": job["stage"],
            "progress": job["progress"],
            "request_id": job["request_id"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
            "error": job["error"]
        }

    def get_results(self, job_id: str) -> Optional[ResultResponse]:
        """Get validation results"""
        return self.results.get(job_id)

    def _create_mock_results(self, job_id: str, request_id: str, bank_code: str):
        """Create realistic mock validation results"""
        bank_profile = next((bp for bp in self.bank_profiles if bp.code == bank_code), self.bank_profiles[0])

        # Create varied findings based on bank type
        findings = []
        score = 85

        if bank_profile.enforcement_level == EnforcementLevel.STRICT:
            findings = [
                Finding(
                    id="finding-1",
                    category="Document Discrepancy",
                    severity=SeverityLevel.CRITICAL,
                    field="Expiry Date",
                    expected="Must include place of expiry",
                    actual="Only date mentioned without place",
                    description="UCP 600 requires both date and place of expiry to be clearly stated",
                    ucp_reference="Article 6(d)(ii)"
                ),
                Finding(
                    id="finding-2",
                    category="Amount Discrepancy",
                    severity=SeverityLevel.WARNING,
                    field="Currency",
                    expected="USD",
                    actual="EUR",
                    description="Invoice currency differs from LC currency",
                    ucp_reference="Article 18(c)"
                )
            ]
            score = 72
        else:
            findings = [
                Finding(
                    id="finding-1",
                    category="Minor Discrepancy",
                    severity=SeverityLevel.INFO,
                    field="Beneficiary Name",
                    expected="Exact match required",
                    actual="Minor spelling variation",
                    description="Beneficiary name has minor spelling differences",
                    ucp_reference="Article 14(f)"
                )
            ]
            score = 91

        correlation_id = f"corr-{str(uuid.uuid4())[:8]}"
        evidence_sha256 = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"

        result = ResultResponse(
            job_id=job_id,
            score=score,
            findings=findings,
            evidence_url=f"/api/evidence/{job_id}/evidence-pack.pdf",
            evidence_sha256=evidence_sha256,
            correlation_id=correlation_id,
            request_id=request_id,
            bank_profile=bank_profile,
            processing_time=2847,  # milliseconds
            quota=self.mock_user["quota"] - 1,
            created_at=datetime.utcnow()
        )

        self.results[job_id] = result

    def get_bank_profiles(self) -> List[BankProfile]:
        """Get all bank profiles"""
        return self.bank_profiles

    def get_current_user(self):
        """Get mock current user"""
        return self.mock_user


# Global instance
db = MockDatabase()