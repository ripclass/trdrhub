# Enhanced Document Validation Layer

## Overview

The enhanced document validation layer for LCopilot provides pre-OCR/LLM validation to ensure document quality and prevent unnecessary processing costs. This layer validates both file types and document content before forwarding to expensive AI services.

## Features

### 1. File-Type Guardrails
- **Supported formats**: PDF, JPG/JPEG, PNG
- **MIME-type validation**: Uses `python-magic` for accurate file type detection
- **Size limits**: Maximum 10MB per file
- **Extension validation**: Checks file extensions for initial filtering

### 2. Document Classification
- **Keyword-based validation**: Matches document content to expected types
- **Supported document types**:
  - `lc`: Letter of Credit
  - `invoice`: Commercial Invoice
  - `packing_list`: Packing List
  - `bl`: Bill of Lading
  - `coo`: Certificate of Origin
  - `insurance`: Insurance Certificate
  - `other`: Generic documents (bypass content validation)

### 3. Content Validation
- **Text extraction**: Uses PyPDF2 for PDFs, pytesseract for images
- **Keyword matching**: Searches for document-specific keywords
- **Suspicious content detection**: Identifies non-trade documents (CVs, bank statements, etc.)
- **Confidence scoring**: Provides match probability scores

### 4. Cost Protection
- **Early rejection**: Invalid documents are rejected before OCR/LLM processing
- **Error categorization**: Structured error responses for frontend handling
- **Audit logging**: Comprehensive validation logging

## API Usage

### Enhanced `/api/validate` Endpoint

```python
POST /api/validate
Content-Type: multipart/form-data

# Required fields
files: List[UploadFile]              # Document files to validate

# Optional fields
user_type: str                       # "exporter" or "importer"
workflow_type: str                   # Workflow identifier
lc_number: str                       # LC reference number
notes: str                           # Additional notes
document_tags: str                   # JSON mapping filename to document type
```

### Document Tags Format

```json
{
  "invoice.pdf": "invoice",
  "packing_list.pdf": "packing_list",
  "bill_of_lading.pdf": "bl",
  "certificate.pdf": "coo",
  "insurance.pdf": "insurance",
  "other_doc.pdf": "other"
}
```

### Response Formats

#### Success Response (200)
```json
{
  "job_id": "uuid-job-id",
  "status": "queued",
  "request_id": "uuid-request-id",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### File Type Error (400)
```json
{
  "detail": {
    "error_id": "document_validation_failed",
    "type": "validation",
    "message": "Document validation failed for 1 file(s)",
    "validation_errors": [
      {
        "error": "File extension .docx not supported. Allowed: .pdf, .jpg, .jpeg, .png",
        "error_type": "invalid_file_type",
        "file": "document.docx",
        "expected": "PDF, JPG, PNG",
        "actual": null,
        "confidence": 1.0
      }
    ]
  }
}
```

#### Content Validation Error (422)
```json
{
  "detail": {
    "error_id": "document_validation_failed",
    "type": "validation",
    "message": "Document validation failed for 1 file(s)",
    "validation_errors": [
      {
        "error": "Document appears to contain non-trade content",
        "error_type": "suspicious_content",
        "file": "cv.pdf",
        "expected": "invoice",
        "actual": null,
        "confidence": 0.85
      }
    ]
  }
}
```

## Testing

### Unit Tests

Run comprehensive unit tests:
```bash
cd /path/to/backend
python -m pytest test_document_validation.py -v
```

### Integration Tests

Run API integration tests:
```bash
# Start the backend server first
python main.py

# Run integration tests
python test_api.py
```

### Test Cases Covered

1. **File Type Validation**
   - Valid PDF files → Accept
   - Invalid extensions (.docx, .xlsx) → Reject (400)
   - Files too large → Reject (400)

2. **Document Content Validation**
   - Valid invoice with keywords → Accept
   - CV uploaded as invoice → Reject (422)
   - Bank statement as invoice → Reject (422)
   - Valid LC document → Accept
   - Valid Bill of Lading → Accept

3. **Edge Cases**
   - Missing document tags → Default to 'other' type
   - Malformed JSON tags → Fallback gracefully
   - Mixed valid/invalid documents → Reject batch
   - Empty files → Handle gracefully

## Keywords by Document Type

### Letter of Credit (lc)
- "letter of credit", "lc no", "lc number"
- "ucp 600", "ucp600", "irrevocable"
- "documentary credit", "issuing bank"
- "advising bank", "beneficiary", "applicant"

### Commercial Invoice (invoice)
- "invoice no", "invoice number", "commercial invoice"
- "pro forma", "seller", "buyer"
- "bill to", "ship to", "total amount"
- "sub total", "tax amount", "freight charges"

### Packing List (packing_list)
- "packing list", "packing slip", "qty", "quantity"
- "gross weight", "net weight", "dimensions"
- "cartons", "packages", "description of goods"
- "total packages", "cbm", "volume"

### Bill of Lading (bl)
- "bill of lading", "b/l", "bl no"
- "shipper", "consignee", "notify party"
- "port of loading", "port of discharge"
- "vessel", "voyage", "container no", "seal no"

### Certificate of Origin (coo)
- "certificate of origin", "origin certificate"
- "country of origin", "chamber of commerce"
- "export declaration", "preferential origin"
- "gstp", "fta", "rules of origin"

### Insurance Certificate (insurance)
- "insurance policy", "certificate of insurance"
- "marine insurance", "policy number"
- "insured amount", "coverage", "risks covered"
- "underwriters", "claims payable", "survey report"

## Deployment Notes

### Dependencies
Install required packages:
```bash
pip install python-magic PyPDF2 pytesseract Pillow
```

### System Dependencies
- **macOS**: `brew install libmagic`
- **Ubuntu**: `sudo apt-get install libmagic1`
- **For OCR**: `brew install tesseract` or `sudo apt-get install tesseract-ocr`

### Configuration
- File size limits configurable in `DocumentValidator.MAX_FILE_SIZE`
- Keyword thresholds adjustable in classification logic
- MIME type allowlist customizable in `ALLOWED_MIME_TYPES`

## Monitoring

### Validation Metrics
- File type rejection rates
- Content validation accuracy
- Processing time per validation
- Cost savings from early rejection

### Error Categories
- `invalid_file_type`: Wrong file format
- `invalid_document_content`: Content doesn't match expected type
- `suspicious_content`: Non-trade document detected
- `extraction_failed`: Could not extract text content
- `validation_system_error`: Internal system error

## Future Enhancements

1. **ML-based Classification**: Train models for more accurate document type detection
2. **OCR Confidence Scoring**: Use OCR confidence for validation decisions
3. **Multi-language Support**: Extend keywords to other languages
4. **Custom Rules**: Allow customer-specific validation rules
5. **Performance Optimization**: Cache text extraction results

## Troubleshooting

### Common Issues

1. **python-magic not working**:
   - Install system libmagic library
   - Use alternative MIME detection fallback

2. **OCR failures**:
   - Ensure tesseract is installed
   - Check image quality and format

3. **False positives/negatives**:
   - Review keyword lists
   - Adjust confidence thresholds
   - Add customer-specific keywords

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show validation decisions, keyword matches, and confidence scores.