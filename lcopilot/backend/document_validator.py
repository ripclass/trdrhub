"""
Enhanced Document Validation Layer for LCopilot
Implements pre-OCR/LLM validation to prevent cost and ensure document quality

Features:
1. File-type guardrails with MIME-type validation
2. Document classification validation using keyword matching
3. Cost protection by rejecting invalid documents early
4. Support for both Exporter and Importer workflows
"""

import mimetypes
import io
import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# PDF text extraction
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# OCR for images (optional fast extraction)
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Supported document types with expected keywords"""
    LC = "lc"
    INVOICE = "invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bl"
    CERTIFICATE_OF_ORIGIN = "coo"
    INSURANCE = "insurance"
    OTHER = "other"


class ValidationResult(str, Enum):
    """Document validation results"""
    VALID = "valid"
    INVALID_FILE_TYPE = "invalid_file_type"
    INVALID_DOCUMENT_CONTENT = "invalid_document_content"
    EXTRACTION_FAILED = "extraction_failed"
    SUSPICIOUS_CONTENT = "suspicious_content"


@dataclass
class DocumentValidationError:
    """Structured error information for validation failures"""
    error_type: str
    file: str
    expected: str
    actual: Optional[str] = None
    message: str = ""
    confidence: float = 0.0


@dataclass
class DocumentClassificationResult:
    """Result of document type classification"""
    result: ValidationResult
    confidence: float
    detected_type: Optional[DocumentType] = None
    keywords_found: List[str] = None
    error: Optional[DocumentValidationError] = None


class DocumentValidator:
    """Enhanced document validator with file-type and content validation"""

    # Allowed file types
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/jpg'
    }

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Document type keywords for classification
    DOCUMENT_KEYWORDS = {
        DocumentType.LC: [
            "letter of credit", "lc no", "lc number", "ucp 600", "ucp600",
            "irrevocable", "documentary credit", "credit number", "l/c",
            "issuing bank", "advising bank", "beneficiary", "applicant"
        ],
        DocumentType.INVOICE: [
            "invoice no", "invoice number", "commercial invoice", "pro forma",
            "invoice date", "seller", "buyer", "bill to", "ship to",
            "total amount", "sub total", "tax amount", "freight charges"
        ],
        DocumentType.PACKING_LIST: [
            "packing list", "packing slip", "qty", "quantity", "pieces",
            "gross weight", "net weight", "dimensions", "cartons", "packages",
            "description of goods", "total packages", "cbm", "volume"
        ],
        DocumentType.BILL_OF_LADING: [
            "bill of lading", "b/l", "bl no", "shipper", "consignee",
            "notify party", "port of loading", "port of discharge",
            "vessel", "voyage", "container no", "seal no", "freight"
        ],
        DocumentType.CERTIFICATE_OF_ORIGIN: [
            "certificate of origin", "origin certificate", "country of origin",
            "chamber of commerce", "export declaration", "preferential origin",
            "non-preferential", "gstp", "fta", "rules of origin"
        ],
        DocumentType.INSURANCE: [
            "insurance policy", "certificate of insurance", "marine insurance",
            "policy number", "insured amount", "coverage", "risks covered",
            "underwriters", "claims payable", "survey report"
        ]
    }

    # Suspicious content patterns (non-trade documents)
    SUSPICIOUS_PATTERNS = [
        # Personal documents
        r"\b(?:curriculum vitae|resume|cv)\b",
        r"\b(?:personal statement|cover letter)\b",
        r"\b(?:birth certificate|passport|visa)\b",

        # Financial but non-trade
        r"\b(?:bank statement|credit report|loan)\b",
        r"\b(?:tax return|w-2|1099)\b",
        r"\b(?:payroll|salary|wages)\b",

        # Academic documents
        r"\b(?:transcript|diploma|degree)\b",
        r"\b(?:research paper|thesis|dissertation)\b",

        # Legal but non-trade
        r"\b(?:will|testament|deed|lease)\b",
        r"\b(?:court|lawsuit|litigation)\b",

        # Medical
        r"\b(?:medical record|prescription|diagnosis)\b",
        r"\b(?:patient|doctor|hospital)\b",

        # Other business but non-trade
        r"\b(?:employment contract|hr policy)\b",
        r"\b(?:marketing plan|business plan)\b"
    ]

    def __init__(self):
        """Initialize the document validator"""
        self.magic_mime = None
        # Initialize python-magic for MIME type detection (disabled for mock backend)
        # self.magic_mime = magic.Magic(mime=True)

    def validate_file_type(self, file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file type using both extension and MIME type detection

        Args:
            file_content: Binary file content
            filename: Original filename

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            return False, f"File size {len(file_content)} bytes exceeds maximum {self.MAX_FILE_SIZE} bytes"

        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File extension {file_ext} not supported. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"

        # Check MIME type using mimetypes module (fallback for mock backend)
        try:
            guessed_type, _ = mimetypes.guess_type(filename)
            if guessed_type and guessed_type not in self.ALLOWED_MIME_TYPES:
                return False, f"File MIME type {guessed_type} not supported. Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
        except Exception as e:
            logger.warning(f"MIME type detection failed: {e}")

        return True, None

    def extract_text_content(self, file_content: bytes, filename: str, max_pages: int = 2) -> str:
        """
        Extract text content from file for keyword analysis

        Args:
            file_content: Binary file content
            filename: Original filename
            max_pages: Maximum pages to extract (for PDFs)

        Returns:
            Extracted text content
        """
        file_ext = Path(filename).suffix.lower()
        text_content = ""

        try:
            if file_ext == '.pdf':
                # Extract text from PDF using PyPDF2
                if PyPDF2:
                    pdf_file = io.BytesIO(file_content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)

                    pages_to_read = min(len(pdf_reader.pages), max_pages)
                    for i in range(pages_to_read):
                        page = pdf_reader.pages[i]
                        text_content += page.extract_text() + "\n"
                else:
                    logger.warning("PyPDF2 not available for PDF text extraction")

            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # Extract text from images using OCR
                if pytesseract and Image:
                    image = Image.open(io.BytesIO(file_content))
                    text_content = pytesseract.image_to_string(image)
                else:
                    logger.warning("pytesseract/PIL not available for OCR")

        except Exception as e:
            logger.warning(f"Text extraction failed for {filename}: {e}")

        return text_content.lower().strip()

    def classify_document_type(self, text_content: str, expected_type: DocumentType) -> DocumentClassificationResult:
        """
        Classify document type based on extracted text content

        Args:
            text_content: Extracted text from document
            expected_type: User-specified document type

        Returns:
            DocumentClassificationResult with classification details
        """
        if not text_content:
            return DocumentClassificationResult(
                result=ValidationResult.EXTRACTION_FAILED,
                confidence=0.0,
                error=DocumentValidationError(
                    error_type="extraction_failed",
                    file="",
                    expected=expected_type.value,
                    message="Could not extract text content from document"
                )
            )

        # Check for suspicious non-trade content
        suspicious_score = self._check_suspicious_content(text_content)
        if suspicious_score > 0.7:
            return DocumentClassificationResult(
                result=ValidationResult.SUSPICIOUS_CONTENT,
                confidence=suspicious_score,
                error=DocumentValidationError(
                    error_type="suspicious_content",
                    file="",
                    expected=expected_type.value,
                    message="Document appears to contain non-trade content"
                )
            )

        # Calculate keyword match scores for all document types
        type_scores = {}
        keywords_found = {}

        for doc_type, keywords in self.DOCUMENT_KEYWORDS.items():
            score, found_keywords = self._calculate_keyword_score(text_content, keywords)
            type_scores[doc_type] = score
            keywords_found[doc_type] = found_keywords

        # Find the best matching document type
        best_match_type = max(type_scores, key=type_scores.get)
        best_match_score = type_scores[best_match_type]
        expected_score = type_scores[expected_type]

        # Determine validation result
        if expected_score >= 0.3:  # Minimum threshold for expected type
            # Expected type has sufficient keywords
            return DocumentClassificationResult(
                result=ValidationResult.VALID,
                confidence=expected_score,
                detected_type=expected_type,
                keywords_found=keywords_found[expected_type]
            )
        elif best_match_score > 0.7 and best_match_type != expected_type:
            # Strong match with different type
            return DocumentClassificationResult(
                result=ValidationResult.INVALID_DOCUMENT_CONTENT,
                confidence=1.0 - expected_score,
                detected_type=best_match_type,
                keywords_found=keywords_found[best_match_type],
                error=DocumentValidationError(
                    error_type="invalid_document_content",
                    file="",
                    expected=expected_type.value,
                    actual=best_match_type.value,
                    message=f"Document appears to be {best_match_type.value} but expected {expected_type.value}"
                )
            )
        else:
            # No strong match found
            return DocumentClassificationResult(
                result=ValidationResult.INVALID_DOCUMENT_CONTENT,
                confidence=1.0 - expected_score,
                detected_type=None,
                keywords_found=keywords_found[expected_type],
                error=DocumentValidationError(
                    error_type="invalid_document_content",
                    file="",
                    expected=expected_type.value,
                    message=f"Document does not contain expected {expected_type.value} keywords"
                )
            )

    def _calculate_keyword_score(self, text_content: str, keywords: List[str]) -> Tuple[float, List[str]]:
        """
        Calculate keyword match score for a document type

        Args:
            text_content: Document text content (lowercase)
            keywords: List of keywords to search for

        Returns:
            Tuple of (score, found_keywords)
        """
        found_keywords = []
        total_weight = 0

        for keyword in keywords:
            if keyword in text_content:
                found_keywords.append(keyword)
                # Weight longer keywords more heavily
                weight = len(keyword.split())
                total_weight += weight

        # Calculate score based on found keywords and their weights
        max_possible_weight = sum(len(kw.split()) for kw in keywords)
        score = total_weight / max_possible_weight if max_possible_weight > 0 else 0

        return score, found_keywords

    def _check_suspicious_content(self, text_content: str) -> float:
        """
        Check for suspicious non-trade content patterns

        Args:
            text_content: Document text content (lowercase)

        Returns:
            Suspicion score (0-1, higher is more suspicious)
        """
        suspicious_matches = 0
        total_patterns = len(self.SUSPICIOUS_PATTERNS)

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                suspicious_matches += 1

        return suspicious_matches / total_patterns if total_patterns > 0 else 0

    def validate_document_type(self, file_content: bytes, filename: str,
                             document_type: str) -> DocumentClassificationResult:
        """
        Complete document validation including file type and content classification

        Args:
            file_content: Binary file content
            filename: Original filename
            document_type: User-specified document type tag

        Returns:
            DocumentClassificationResult with validation outcome
        """
        # Step 1: Validate file type
        is_valid_file, file_error = self.validate_file_type(file_content, filename)
        if not is_valid_file:
            return DocumentClassificationResult(
                result=ValidationResult.INVALID_FILE_TYPE,
                confidence=1.0,
                error=DocumentValidationError(
                    error_type="invalid_file_type",
                    file=filename,
                    expected="PDF, JPG, PNG",
                    message=file_error
                )
            )

        # Step 2: Parse document type
        try:
            expected_type = DocumentType(document_type.lower())
        except ValueError:
            expected_type = DocumentType.OTHER

        # Skip content validation for 'other' type
        if expected_type == DocumentType.OTHER:
            return DocumentClassificationResult(
                result=ValidationResult.VALID,
                confidence=1.0,
                detected_type=DocumentType.OTHER
            )

        # Step 3: Extract text content
        text_content = self.extract_text_content(file_content, filename)

        # Step 4: Classify document type
        classification_result = self.classify_document_type(text_content, expected_type)

        # Update error with filename
        if classification_result.error:
            classification_result.error.file = filename

        return classification_result


# Convenience functions for FastAPI integration
def create_validation_error_response(error: DocumentValidationError) -> Dict:
    """Create standardized error response for API"""
    return {
        "error": error.message,
        "error_type": error.error_type,
        "file": error.file,
        "expected": error.expected,
        "actual": error.actual,
        "confidence": error.confidence
    }


def validate_uploaded_files(files: List, document_tags: Dict[str, str]) -> List[Dict]:
    """
    Validate multiple uploaded files with their document type tags

    Args:
        files: List of UploadFile objects from FastAPI
        document_tags: Mapping of filename to document type

    Returns:
        List of validation errors (empty if all valid)
    """
    validator = DocumentValidator()
    errors = []

    for file in files:
        # Get document type tag for this file
        doc_type = document_tags.get(file.filename, 'other')

        try:
            # Read file content
            file_content = file.file.read()
            file.file.seek(0)  # Reset file pointer

            # Validate document
            result = validator.validate_document_type(file_content, file.filename, doc_type)

            if result.result != ValidationResult.VALID:
                errors.append(create_validation_error_response(result.error))

        except Exception as e:
            logger.error(f"Validation failed for {file.filename}: {e}")
            errors.append({
                "error": f"Validation failed: {str(e)}",
                "error_type": "validation_error",
                "file": file.filename,
                "expected": doc_type,
                "actual": None,
                "confidence": 0.0
            })

    return errors