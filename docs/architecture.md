Fullstack Architecture Document: LCopilot
1. Introduction
This document outlines the complete fullstack architecture for LCopilot, including backend systems, frontend implementation, and their integration1. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack2.
Starter Template or Existing Project
This is a greenfield project with a specified FastAPI (Python) backend and React frontend3. To accelerate setup and enforce consistency, the following approach will be used:
Monorepo Tool: Use Turborepo for a high-performance build system.
Frontend Starter: Initialize using the standard Vite + React (TypeScript) template.
Backend Structure: Use a standard, community-accepted FastAPI project structure.

2. High-Level Architecture
Technical Summary
The architecture will be a serverless fullstack application in a monorepo. The frontend will be a
React Single-Page Application (SPA) hosted on Vercel4. The backend will be a
monolithic FastAPI (Python) service deployed as a serverless function on AWS5. An asynchronous, queue-based processing model will be used for long-running tasks like OCR to ensure API responsiveness. This approach prioritizes rapid development, low operational overhead, and scalability6.
Platform and Infrastructure Choice
Platform: A combination of Vercel for the frontend and AWS for the backend7.
Key Services:
Vercel: Hosting, CI/CD, and CDN for the React frontend8.
AWS Lambda + API Gateway: For hosting the serverless FastAPI backend9.
Amazon S3: For direct, secure file uploads and report storage.
Amazon SQS: For decoupling the API from the asynchronous worker.
Amazon RDS (PostgreSQL): For the managed relational database10.
High-Level Architecture Diagram
This diagram shows the asynchronous flow, which solves file size limits and timeouts by keeping the API thin and fast.
Code snippet
graph TD
    A[User (SPA on Vercel)] -->|Auth + UI| B[Vercel CDN]
    B --> C[React SPA]
    C -->|GET pre-signed URL| D[API Gateway]
    D --> E[Lambda: FastAPI API]
    C -->|PUT file| S3[(S3 Uploads - KMS)]
    E -->|Enqueue job meta| Q[(SQS Jobs)]
    W[Worker (Lambda or ECS Fargate)]
    Q --> W
    W -->|Get file| S3
    W -->|OCR DocAI/Textract| O[[OCR Vendors]]
    W -->|Rules Engine + Report| RDS[(Amazon RDS Postgres)]
    W -->|Write PDF| SP[(S3 Reports - KMS)]
    C -->|Poll/WS for status| E
    E -->|Return report link| C


3. Tech Stack
This table outlines the specific technologies and the known risks or "guardrails" for each choice.
Category
Technology
Version
Risks & Mitigations (Guardrails)
Monorepo Tool
Turborepo
latest
Risk: Devs unfamiliar with config. Mitigation: Keep config minimal; add README with common commands.
Frontend Framework
React
18.x
Risk: Less suited for SEO than Next.js. Mitigation: MVP is a tool, not a content site; this is acceptable.
Backend Framework
FastAPI (Python)
latest
Risk: Cold starts. Mitigation: Keep Lambda app small; move heavy compute to async workers.
Database
PostgreSQL
15.x
Risk: Connection exhaustion from Lambdas. Mitigation: Use RDS Proxy from day one.
File Storage
Amazon S3
N/A
Risk: Large file uploads. Mitigation: Enforce client-side size validation; use direct-to-S3 pre-signed URLs.
Async Messaging
Amazon SQS
N/A
Risk: Misconfigured timeouts causing job re-runs. Mitigation: Set timeouts longer than max OCR run; use idempotency keys.
Styling
Tailwind CSS
latest
Risk: Bangla font rendering issues. Mitigation: Ship a custom Unicode-safe font stack; test Bangla UI thoroughly.
PDF Generation
WeasyPrint
latest
Risk: Complex layouts may render differently. Mitigation: Build a canonical report.css; use screenshot tests in CI.
E2E Testing
Playwright
latest
Risk: Slow CI runs. Mitigation: Restrict to critical path smoke tests for the MVP.


4. Data Models
The data model is structured to capture the entire validation lifecycle and ensure auditability.
User: Manages user accounts.
ValidationSession: The central container for a single validation job.
Document: Represents a single user-uploaded file and its metadata.
Discrepancy: Represents a single issue flagged by the engine.
Report: Represents the final, versioned PDF output of a session, ensuring immutability.

5. API Specification
A REST API is the most pragmatic approach, as FastAPI natively generates the required OpenAPI specification.
POST /auth/register: Register a new user.
POST /auth/login: Log in and receive a JWT.
POST /sessions: Create a new validation session and get pre-signed URLs for document uploads.
GET /sessions: List all past validation sessions for the logged-in user.
GET /sessions/{sessionId}: Get the status and results of a validation session.
GET /sessions/{sessionId}/report: Get a pre-signed URL to download the final report PDF.

6. Components
The architecture is composed of six primary logical components with a clear separation of concerns.
Frontend SPA (React): Handles all user interaction.
Backend API (FastAPI): Acts as the thin, synchronous control plane for auth and session management.
Validation Worker (Lambda/Fargate): The asynchronous workhorse for OCR, rules, and report generation.
Database (PostgreSQL/RDS): The single source of truth for all persistent state.
Storage Service (S3): Provides secure storage for uploads and reports.
Queue Service (SQS): Decouples the API from the long-running worker.

7. External APIs
The MVP's core functionality relies on a dual-engine OCR strategy using an Adapter Pattern to abstract the vendors. The OCRManager will orchestrate calls to concrete OCREngine implementations, normalizing their results.
Google Cloud Vision (Document AI): Primary OCR engine.
AWS Textract: Secondary OCR engine for fallback and comparison.

8. Core Workflows
The primary workflow is asynchronous to handle long-running tasks and large files gracefully, with explicit error handling paths using SQS Dead Letter Queues (DLQs) for failed jobs.

9. Database Schema
A normalized PostgreSQL schema will be used, defined and managed with a migration tool (Alembic) from day one. To protect the audit trail, critical tables like validation_sessions and reports will use a soft-delete pattern (deleted_at column) instead of ON DELETE CASCADE.

10. Source Tree
The project will use a Turborepo monorepo structure, separating deployable apps (api, web) from shared packages (shared-types, ui). Note: For the MVP, the asynchronous worker logic will reside within the apps/api project to accelerate development, with a plan to refactor it into a dedicated apps/worker application post-MVP for independent scaling.

11. Infrastructure and Deployment
Infrastructure as Code: AWS CDK will be used to define and provision all AWS resources.
CI/CD: GitHub Actions will orchestrate a backend-first deployment. The backend CDK stack is deployed to AWS, and only upon its successful completion is the Vercel frontend deployment triggered. This prevents frontend/backend version mismatches.

12. Error Handling Strategy
A standardized JSON error format and a unique correlationId will be used for every request to ensure traceability. Sentry will be integrated into both the frontend and backend to provide full-stack error reporting and visibility into client-side issues.

13. Coding Standards
Standards will be enforced automatically via linters (ESLint, Flake8), formatters (Prettier, Black), pre-commit hooks (Husky), and CI pipeline checks. Key architectural rules, such as using the packages/shared-types and the centralized API client, will be enforced with custom linting rules where possible.

14. Checklist Results
After a thorough review using the internal architect-checklist, this architecture is deemed complete and robust for the MVP. It aligns with all functional and non-functional requirements, addresses key risks with pragmatic mitigations, and provides a clear, scalable blueprint for development.

15. Next Steps
This architecture document provides the definitive technical blueprint. The next logical step is for the Product Owner (po) to perform a final validation of all artifacts (Project Brief, PRD, and this Architecture Document) to ensure complete alignment before development begins.
