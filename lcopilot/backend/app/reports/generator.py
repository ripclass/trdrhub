"""
PDF report generator using WeasyPrint.
"""

import os
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4
from io import BytesIO
from pathlib import Path

import boto3
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from botocore.exceptions import ClientError

from .templates import ReportTemplate
from ..rules.models import DocumentValidationSummary
from ..models import Report, ValidationSession, User


class ReportGenerator:
    """Professional PDF report generator for validation results."""

    def __init__(self):
        self.template = ReportTemplate()
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'lcopilot-documents')
        self.region = os.getenv('AWS_REGION', 'us-east-1')

        # Setup font configuration for better Bangla support
        self.font_config = FontConfiguration()
        self.static_dir = Path(__file__).parent.parent.parent / "static"

        # CSS for professional styling and font embedding
        self.professional_css = self._load_professional_css()
    
    async def generate_report(
        self,
        summary: DocumentValidationSummary,
        session: ValidationSession,
        user: User,
        language: str = "en"
    ) -> Report:
        """
        Generate PDF report and upload to S3.
        
        Args:
            summary: Validation results summary
            session: Validation session
            user: User who requested the report
            language: Report language ("en" or "bn")
            
        Returns:
            Report model with S3 information
        """
        
        # Prepare session details for the template
        session_details = {
            'user_name': user.full_name,
            'user_email': user.email,
            'session_created_at': session.created_at,
            'processing_time_ms': summary.processing_time_ms
        }
        
        # Generate HTML content
        html_content = self.template.generate_report_html(
            summary=summary,
            session_details=session_details,
            language=language
        )
        
        # Generate PDF from HTML with language support
        pdf_buffer = self._html_to_pdf(html_content, language)
        
        # Upload to S3
        report_id = uuid4()
        s3_key = f"reports/{session.id}/{report_id}.pdf"
        
        file_size = await self._upload_to_s3(pdf_buffer, s3_key)
        
        # Create Report record
        report = Report(
            id=report_id,
            validation_session_id=session.id,
            report_version=1,  # TODO: Handle versioning
            s3_key=s3_key,
            file_size=file_size,
            total_discrepancies=summary.failed_rules,
            critical_discrepancies=summary.critical_issues,
            major_discrepancies=summary.major_issues,
            minor_discrepancies=summary.minor_issues,
            generated_by_user_id=user.id
        )
        
        return report
    
    def _load_professional_css(self) -> CSS:
        """Load professional CSS with embedded fonts."""

        # Path to CSS file
        css_path = self.static_dir / "css" / "reports.css"

        if css_path.exists():
            # Load external CSS file
            return CSS(filename=str(css_path))
        else:
            # Fallback inline CSS
            return CSS(string="""
            @page {
                size: A4;
                margin: 1.5cm 2cm;
            }

            body {
                font-family: 'Inter', 'Noto Sans Bengali', Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.5;
                color: #1f2937;
            }

            .bangla {
                font-family: 'Noto Sans Bengali', Arial, sans-serif;
                font-feature-settings: "liga" 1, "clig" 1, "kern" 1;
            }
            """)

    def _html_to_pdf(self, html_content: str, language: str = "en") -> BytesIO:
        """Convert HTML content to PDF using WeasyPrint with professional styling."""

        try:
            # Create WeasyPrint HTML object with proper base URL
            html_obj = HTML(string=html_content, base_url=str(self.static_dir))

            # Generate PDF with professional CSS and font configuration
            pdf_buffer = BytesIO()

            # Use a more compatible approach
            document = html_obj.render(
                stylesheets=[self.professional_css],
                font_config=self.font_config
            )
            document.write_pdf(pdf_buffer)
            pdf_buffer.seek(0)

            return pdf_buffer

        except Exception as e:
            # Fallback to basic PDF generation without font config
            print(f"Warning: Advanced PDF generation failed, using fallback mode: {str(e)}")

            html_obj = HTML(string=html_content, base_url=str(self.static_dir))
            pdf_buffer = BytesIO()
            html_obj.write_pdf(pdf_buffer, stylesheets=[self.professional_css])
            pdf_buffer.seek(0)
            return pdf_buffer
    
    async def _upload_to_s3(self, pdf_buffer: BytesIO, s3_key: str) -> int:
        """Upload PDF to S3 and return file size."""
        
        try:
            # Get file size
            pdf_buffer.seek(0, 2)  # Seek to end
            file_size = pdf_buffer.tell()
            pdf_buffer.seek(0)  # Reset to beginning
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=pdf_buffer,
                ContentType='application/pdf',
                ServerSideEncryption='AES256',
                Metadata={
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'generator': 'lcopilot-api'
                }
            )
            
            return file_size

        except ClientError as e:
            raise Exception(f"Failed to upload report to S3: {str(e)}")

    def get_font_paths(self) -> Dict[str, str]:
        """Get paths to embedded fonts."""
        fonts_dir = self.static_dir / "fonts"
        return {
            'noto_bengali_regular': str(fonts_dir / "NotoSansBengali-Regular.ttf"),
            'noto_bengali_bold': str(fonts_dir / "NotoSansBengali-Bold.ttf")
        }
    
    def generate_sample_report(self, language: str = "en") -> str:
        """Generate a sample HTML report for testing."""
        from uuid import UUID
        from ..rules.models import (
            DocumentValidationSummary, ValidationResult, ValidationRule,
            ValidationStatus, FieldType, FieldComparison, ExtractedField
        )
        from ..models import DiscrepancySeverity, DocumentType

        # Create sample validation rules and results
        sample_rules = [
            ValidationRule(
                rule_id="FF001",
                rule_name="LC Expiry Date Future" if language == "en" else "এলসি মেয়াদ ভবিষ্যতে",
                description="LC expiry date must be in the future" if language == "en" else "এলসি মেয়াদ ভবিষ্যতে থাকতে হবে",
                field_type=FieldType.DATE,
                severity=DiscrepancySeverity.CRITICAL
            ),
            ValidationRule(
                rule_id="AM002",
                rule_name="Amount Consistency" if language == "en" else "পরিমাণের সামঞ্জস্য",
                description="Invoice amount should not exceed LC amount" if language == "en" else "ইনভয়েস পরিমাণ এলসি পরিমাণ অতিক্রম করা উচিত নয়",
                field_type=FieldType.AMOUNT,
                severity=DiscrepancySeverity.MAJOR
            )
        ]

        sample_results = [
            ValidationResult(
                rule=sample_rules[0],
                status=ValidationStatus.FAILED,
                message="LC has expired on 2023-12-01" if language == "en" else "এলসি ২০২৩-১২-০১ তারিখে মেয়াদ শেষ হয়েছে",
                expected_value="Future date" if language == "en" else "ভবিষ্যৎ তারিখ",
                actual_value="2023-12-01",
                confidence=0.95,
                affected_documents=[DocumentType.LETTER_OF_CREDIT]
            ),
            ValidationResult(
                rule=sample_rules[1],
                status=ValidationStatus.FAILED,
                message="Invoice amount exceeds LC amount" if language == "en" else "ইনভয়েস পরিমাণ এলসি পরিমাণ অতিক্রম করেছে",
                expected_value="≤ $95,000.00",
                actual_value="$100,000.00",
                confidence=0.88,
                affected_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.LETTER_OF_CREDIT]
            )
        ]

        sample_comparisons = [
            FieldComparison(
                field_name="Amount" if language == "en" else "পরিমাণ",
                field_type=FieldType.AMOUNT,
                lc_field=ExtractedField(
                    field_name="lc_amount",
                    field_type=FieldType.AMOUNT,
                    value="$95,000.00",
                    confidence=0.95,
                    document_type=DocumentType.LETTER_OF_CREDIT
                ),
                invoice_field=ExtractedField(
                    field_name="invoice_amount",
                    field_type=FieldType.AMOUNT,
                    value="$100,000.00",
                    confidence=0.90,
                    document_type=DocumentType.COMMERCIAL_INVOICE
                ),
                bl_field=ExtractedField(
                    field_name="bl_amount",
                    field_type=FieldType.AMOUNT,
                    value="$100,000.00",
                    confidence=0.92,
                    document_type=DocumentType.BILL_OF_LADING
                ),
                is_consistent=False,
                discrepancies=[]
            ),
            FieldComparison(
                field_name="Goods Description" if language == "en" else "পণ্যের বিবরণ",
                field_type=FieldType.TEXT,
                lc_field=ExtractedField(
                    field_name="goods_description",
                    field_type=FieldType.TEXT,
                    value="Cotton Fabrics",
                    confidence=0.98,
                    document_type=DocumentType.LETTER_OF_CREDIT
                ),
                invoice_field=ExtractedField(
                    field_name="goods_description",
                    field_type=FieldType.TEXT,
                    value="Cotton Fabrics",
                    confidence=0.95,
                    document_type=DocumentType.COMMERCIAL_INVOICE
                ),
                bl_field=ExtractedField(
                    field_name="goods_description",
                    field_type=FieldType.TEXT,
                    value="Cotton Fabrics",
                    confidence=0.93,
                    document_type=DocumentType.BILL_OF_LADING
                ),
                is_consistent=True,
                discrepancies=[]
            )
        ]

        sample_summary = DocumentValidationSummary(
            session_id=UUID('12345678-1234-5678-9012-123456789012'),
            total_rules=8,
            passed_rules=6,
            failed_rules=2,
            warnings=1,
            critical_issues=1,
            major_issues=1,
            minor_issues=0,
            validation_results=sample_results,
            field_comparisons=sample_comparisons,
            processing_time_ms=2150,
            validated_at=datetime.now(timezone.utc)
        )

        session_details = {
            'user_name': 'জন ডো' if language == "bn" else 'John Doe',
            'user_email': 'john.doe@example.com',
            'session_created_at': datetime.now(timezone.utc),
            'processing_time_ms': 2150
        }

        return self.template.generate_report_html(
            summary=sample_summary,
            session_details=session_details,
            language=language
        )

    def generate_sample_pdf(self, language: str = "en", output_path: str = None) -> str:
        """Generate a sample PDF report for testing and save to file."""

        # Generate HTML content
        html_content = self.generate_sample_report(language)

        # Convert to PDF
        pdf_buffer = self._html_to_pdf(html_content, language)

        # Save to file
        if not output_path:
            output_path = f"/tmp/lcopilot_sample_report_{language}.pdf"

        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        return output_path