# LCopilot Frontend - How to Run

## Prerequisites
- Node.js 18+ installed
- Backend API running on http://localhost:5000

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open browser to http://localhost:3000
```

## Build for Production

```bash
# Build the app
npm run build

# Preview production build
npm run preview
```

## Run Tests

```bash
# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage
```

## Environment Variables

Create `.env.local` file:

```env
VITE_API_URL=http://localhost:5000/api
```

## Key Features Implemented

✅ **Routes**
- `/validate` - Upload and validate LC documents
- `/jobs/:jobId` - Track processing progress
- `/results/:jobId` - View validation results
- `/pricing` - Pricing tiers
- `/billing/callback` - Payment callback

✅ **Components**
- UploadBox - Drag-drop file upload with validation
- BankSelect - Bank profile selection
- ProgressStrip - Job progress indicator
- ResultPanels - SME/Bank style results
- QuotaBadge - Credit tracking
- ErrorToast - Global error notifications
- RateLimitNotice - 429 handling

✅ **Features**
- Mobile-first responsive design (390px verified)
- React Query for API state management
- Error boundary for crash protection
- PWA support with offline caching
- TypeScript for type safety

## API Integration

The app expects these backend endpoints:
- `POST /api/validate` - Submit validation
- `GET /api/jobs/:id` - Poll job status
- `GET /api/results/:id` - Get results
- `GET /api/profiles/banks` - Bank profiles
- `POST /api/pay/sslcommerz/session` - Start payment
- `GET /api/pay/sslcommerz/callback` - Payment callback

## Development Notes

- File size limit: 10MB
- Supported formats: PDF, JPG, PNG, JSON
- Job polling: 2s intervals
- Rate limit handling with friendly UX
- Request IDs tracked for debugging