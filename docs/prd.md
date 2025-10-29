Product Requirements Document (PRD): LCopilot
1. Goals and Background Context
Goals
For Users: To drastically reduce the time and anxiety involved in validating Letters of Credit, eliminate costly errors, and accelerate payment cycles.
For the Business: To successfully launch a focused MVP within 8-10 weeks to validate the core assumption that Bangladeshi SMEs will pay for a specialized, AI-powered compliance tool.
Background Context
SMEs in Bangladesh's export sector currently rely on slow, expensive, and error-prone manual processes to validate Letters of Credit. A single discrepancy can lead to payment rejections, shipment delays, and significant fees, directly impacting their cash flow and profitability. LCopilot addresses this by providing an instant, accurate, and automated validation service that transforms compliance from a business risk into a source of confidence.
Non-Goals (Explicitly Out of Scope for MVP)
Enterprise/Banks: Features tailored for banks or large corporations (e.g., integration into trade finance systems, enterprise dashboards).
Advanced Document Types: Validation of secondary docs such as insurance, certificates of origin, packing lists.
Full ISBP Coverage: Comprehensive rule library beyond the “fatal four.”
Advisory Intelligence: “Soft warning” insights, recommendations, or optimization suggestions.
Complex Integrations: No external integrations with freight forwarders, customs agents, or ERP systems.
Mobile App: Fully native iOS/Android apps are out of scope; MVP is responsive web only.
Change Log
Date
Version
Description
Author
2025-09-11
1.0
Initial PRD Draft
John (pm)


2. Requirements
Functional Requirements (FR)
FR1: The system must allow a user to upload a Letter of Credit, a Commercial Invoice, and a Bill of Lading in PDF and common image formats.
FR2: The system must use Optical Character Recognition (OCR) to extract key data fields from the uploaded documents.
FR3: The system must validate the extracted data against a core set of deterministic rules based on UCP 600, focusing on Dates, Amounts, Parties, and Ports.
FR4: The system must perform cross-document consistency checks for key fields (e.g., amounts, ports) between the uploaded documents.
FR5: The system must generate a downloadable PDF report summarizing all findings.
FR6: The PDF report must clearly list all identified discrepancies.
FR7: The report must include a checklist of all documents required by the LC and their validation status.
FR8: The report must display a summary of key deadlines.
FR9: The system must provide a simple, linear workflow from document upload → issue review → report download.
FR10: The system must provide a user-facing visual matrix (Cross-Check Matrix) showing side-by-side field comparisons across documents.
Non-Functional Requirements (NFR)
NFR1: The user interface must be available in both English and Bangla.
NFR2: The web application must be fully responsive and usable on both desktop and mobile browsers.
NFR3: The end-to-end validation process, from document upload to report availability, should feel near-instantaneous to the user (target < 30 seconds).
NFR4: All user-uploaded documents and extracted data must be encrypted both in transit (TLS 1.3) and at rest (AES-256).
NFR5: User-uploaded documents must be automatically and permanently deleted from the system after a defined retention period (e.g., 7 days).
NFR6: The system must maintain an immutable audit log for each validation check.

3. User Interface Design Goals
Overall UX Vision
The user experience must embody the core value proposition: transforming the user's journey from fear and uncertainty to clarity, confidence, and control. The UI should be minimalist, professional, and function-first.
Key Interaction Paradigms
Linear Workflow: The MVP will enforce a strict workflow: Welcome → Upload → Review → Report.
Progressive Disclosure: The system will present a high-level summary first, allowing users to drill down into details to avoid overwhelm.
Core Screens and Views (MVP)
Welcome / Onboarding Screen: A screen to frame the tool, set expectations, provide a sample LC pack, and display privacy reassurances before upload.
Upload Screen: A simple, clear interface to upload the required documents.
Review Screen: A unified view presenting the discrepancy summary and the detailed Cross-Check Matrix.
Report View: A simple preview of the final PDF report with a prominent "Download" button.
Accessibility & Branding
Accessibility: The application should meet WCAG 2.1 Level AA standards.
Branding: The UI will be clean, professional, and use a simple color palette (Green/Red/Yellow) to convey status instantly.

4. Technical Assumptions
Repository Structure: Monorepo
The project will be structured as a Monorepo to maximize development speed and simplify dependency management.
Service Architecture: Monolith
The backend will be developed as a single, monolithic service for the MVP to reduce deployment complexity.
Testing Requirements: Full Testing Pyramid
The project will adhere to a full testing pyramid (Unit, Integration, and E2E tests) to ensure quality.
Risks Associated with Technical Assumptions
Monorepo: Risk of slower CI/CD pipelines as the codebase grows. Mitigated by using lightweight tools like Turborepo.
Monolith: Risk of difficulty in scaling specific bottlenecks. Mitigated by designing with decoupled internal modules.
Full Testing Pyramid: Risk of E2E tests being time-consuming. Mitigated by prioritizing only the critical user flow for E2E testing in the MVP.
Dual-OCR Strategy: Risk of high costs and latency. Mitigated by caching results and allowing user overrides.
LLM for Summaries: Risk of misaligned user expectations. Mitigated by explicitly tagging outputs as "Rule-based check" vs. "AI advisory."

5. Epic List
Epic 1: Foundational Setup & Core Validation Engine.
Epic 2: Multi-Document Consistency & Reporting.
Epic 3: UX, Security & Trust Layer.

6. Epic Details
Epic 1: Foundational Setup & Core Validation Engine
Goal: Establish the core project infrastructure and deliver the fundamental capability to upload a single LC, validate it against the "Fatal Four" rules, and download a basic report.
Story 1.1: Project Scaffolding & CI/CD Setup
Story 1.2: Implement Document Upload UI & Service
Story 1.3: Develop Core OCR & Extraction Service
Story 1.4: Implement the "Fatal Four" Rules Engine
Story 1.5: Display Basic Validation Results
Story 1.6: Generate & Download Basic Report
Story 1.7: Implement Welcome/Onboarding Screen
Epic 2: Multi-Document Consistency & Reporting
Goal: Build upon the core engine to implement cross-document consistency checks and present findings in the Cross-Check Matrix and the final, enhanced PDF report.
Story 2.1: Enhance UI for Multi-Document Upload
Story 2.2: Implement Cross-Document Rules Engine
Story 2.3: Develop the Cross-Check Matrix UI
Story 2.4: Upgrade to the Full Bank-Ready Report (including deadline calculations)
Story 2.5: Handle Multi-Document Upload Errors
Epic 3: UX, Security & Trust Layer
Goal: Wrap the core engine in a secure, trustworthy, and user-friendly experience that meets the specific needs of the Bangladeshi SME market.
Story 3.1: Implement Bilingual Support (English/Bangla)
Story 3.2: Implement Responsive Web Design
Story 3.3: Implement Core Security & Privacy Measures
Story 3.4: Implement Accessibility Standards
Story 3.5: Add Inline Guidance & Help Text
Story 3.6: Implement Clear Error & Empty States

7. Checklist Results Report
After a thorough review using the internal pm-checklist, this PRD is deemed complete, well-structured, and ready for the next phase. The MVP scope is clearly defined, all requirements are testable, and the three-epic structure is logical and incremental.

8. Next Steps
Architect Prompt
"This PRD for LCopilot is complete and approved. Please use it as the single source of truth to create the comprehensive Fullstack Architecture Document. Pay close attention to the Technical Assumptions (Monorepo, Monolith MVP, full testing pyramid) and the non-functional requirements for security, bilingual support, and performance, as these are critical constraints for your design."
