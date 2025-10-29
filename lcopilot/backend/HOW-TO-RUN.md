# LCopilot Mock Backend - How to Run

## Quick Start

```bash
# Navigate to backend directory
cd ~/Desktop/Enso\ Intelligence/trdrhub/lcopilot/backend

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at: **http://localhost:5000**

## API Endpoints

### Core Validation Flow
- `POST /api/validate` - Submit document for validation
- `GET /api/jobs/{jobId}` - Poll job status and progress
- `GET /api/results/{jobId}` - Get validation results

### Supporting Endpoints
- `GET /api/profiles/banks` - List available bank profiles
- `GET /api/me` - Get current user info
- `POST /api/pay/sslcommerz/session` - Create payment session
- `GET /api/pay/sslcommerz/callback` - Payment callback handler

## Test the API

### 1. Upload Document
```bash
curl -X POST http://localhost:5000/api/validate \
  -F "file=@sample.pdf" \
  -F "bankCode=sonali" \
  -F "async=true"

# Response: {"job_id": "uuid", "status": "queued", ...}
```

### 2. Check Job Progress
```bash
curl http://localhost:5000/api/jobs/{job_id}

# Response: {"status": "processing", "stage": "ocr", "progress": 25, ...}
```

### 3. Get Results (once completed)
```bash
curl http://localhost:5000/api/results/{job_id}

# Response: {"score": 85, "findings": [...], "evidence_url": "...", ...}
```

### 4. Get Bank Profiles
```bash
curl http://localhost:5000/api/profiles/banks

# Response: [{"code": "sonali", "name": "Sonali Bank Limited", ...}]
```

## Mock Behavior

### Job Progression Simulation
- **Poll 1-2**: `queued` stage, 5% progress
- **Poll 3-4**: `ocr` stage, 25% progress
- **Poll 5-6**: `rules` stage, 60% progress
- **Poll 7-8**: `evidence` stage, 85% progress
- **Poll 9+**: `done` stage, 100% progress, status = `completed`

### Realistic Mock Data
- **Bank Profiles**: 4 real Bangladesh banks (Sonali, DBBL, HSBC BD, Islami)
- **Findings**: Vary by bank enforcement level (strict/medium/flexible)
- **Scores**: 70-95 based on bank strictness
- **Rate Limiting**: Random 429 responses (1 in 7 requests)

### File Validation
- **Size limit**: 10MB
- **Allowed types**: PDF, JPG, JPEG, PNG, JSON
- **Error responses**: Proper HTTP status codes with error_id

## Frontend Integration

This backend is designed to work with the Phase 5 React frontend:

```bash
# Start backend (terminal 1)
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Start frontend (terminal 2)
cd ../frontend
npm run dev
```

Frontend will be available at http://localhost:3000 and will proxy API requests to the backend.

## Production Notes

This is a **temporary mock backend** for development only. For production:

1. Replace mock database (`db.py`) with PostgreSQL
2. Replace mock OCR/rules with real processing pipeline
3. Add authentication/authorization middleware
4. Add proper logging and monitoring
5. Add rate limiting with Redis
6. Add file storage with S3
7. Add job queuing with SQS/Celery

## Project Structure

```
backend/
├── main.py           # FastAPI application
├── types.py          # Pydantic models
├── db.py            # In-memory mock database
├── requirements.txt  # Python dependencies
└── HOW-TO-RUN.md    # This file
```

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **python-multipart**: File upload support

All designed to be lightweight and easy to replace with production systems.