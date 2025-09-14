# TrdrHub Architecture Overview

> **Current State**: Phase 4.5 - Security-hardened backend with comprehensive regression testing
> **Next Evolution**: Phase 5 - React frontend rewrite with mobile-first design

## Executive Summary

TrdrHub is architected as a scalable, secure trade intelligence platform that began with LCopilot (LC validation) and will expand to multiple trade tools. Our architecture prioritizes security, scalability, and maintainability while keeping costs optimized for SME customers.

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TrdrHub Platform                               │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│   SME Portal UI     │   Admin Dashboard   │      Bank Integration APIs     │
│   (React + TS)      │   (Flask + Jinja)   │        (REST/GraphQL)          │
│   Phase 5           │   Current           │        Current                  │
└─────────┬───────────┴─────────┬───────────┴─────────┬───────────────────────┘
          │                     │                     │
┌─────────▼─────────────────────▼─────────────────────▼───────────────────────┐
│                          API Gateway Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ Rate        │  │ Auth &      │  │ Request     │  │ Circuit         │   │
│  │ Limiting    │  │ Session     │  │ Validation  │  │ Breaker         │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘   │
└─────────┬───────────────────────────────────────────────────────┬─────────┘
          │                                                       │
┌─────────▼───────────────────────────────────────────────────────▼─────────┐
│                         Business Logic Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   LC Validation │  │  Job Processing │  │    Future Tools             │ │
│  │   Engine        │  │  & Tracking     │  │    (HS Code, Container      │ │
│  │                 │  │                 │  │     Tracking, etc.)         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────┬───────────────────────────────────────────────────────┬─────────┘
          │                                                       │
┌─────────▼───────────────────────────────────────────────────────▼─────────┐
│                        Async Processing Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  SQS Message    │  │  Lambda Workers │  │   Status Tracking           │ │
│  │  Queue          │  │  (Textract,     │  │   (Redis + WebSocket)       │ │
│  │                 │  │   OCR, etc.)    │  │                             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────┬───────────────────────────────────────────────────────┬─────────┘
          │                                                       │
┌─────────▼───────────────────────────────────────────────────────▼─────────┐
│                          Data Layer                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ PostgreSQL   │  │ Redis        │  │ S3 Storage   │  │ CloudWatch    │  │
│  │ (Primary)    │  │ (Cache/Jobs) │  │ (Documents)  │  │ (Logs/Metrics)│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Current Implementation (Phase 4.5)

### Core Components

#### 1. SME Portal (Flask Application)
```
sme_portal/
├── app.py                 # Main Flask application
├── routes/
│   ├── validation.py     # LC validation endpoints
│   ├── dashboard.py      # User dashboard
│   └── auth.py          # Authentication
├── templates/           # Jinja2 templates
├── static/             # CSS, JS, images
└── utils/              # Helper functions
```

**Key Features**:
- Document upload with 10MB size limit
- Real-time job status tracking
- Multi-bank profile support
- Tier-based rate limiting
- Session management with Redis

#### 2. Trust Platform Engine
```
trust_platform/
├── lc_validator.py      # Core validation logic
├── bank_profiles/       # Bank-specific rules
├── document_parser.py   # Document extraction
├── compliance_checker.py # UCP 600 validation
└── evidence_generator.py # Report generation
```

**Capabilities**:
- 95% accuracy in LC document parsing
- Support for 3 major Bangladesh banks
- UCP 600 compliance checking
- Tamper-proof evidence pack generation

#### 3. Async Processing Pipeline
```
async/
├── queue_producer.py    # SQS job creation
├── job_status.py       # Status tracking
├── rate_limiter.py     # Tier-based limits
└── lambda_handler.py   # AWS Lambda worker
```

**Architecture**:
- SQS for reliable job queuing
- Lambda functions for scalable processing
- Redis for real-time status updates
- Automatic failover to Textract OCR

#### 4. OCR Processing
```
ocr/
├── textract_fallback.py # AWS Textract integration
├── pypdf_processor.py   # Primary PDF processing
└── ocr_coordinator.py   # Smart routing logic
```

**Processing Flow**:
1. Primary: pypdf for fast, cost-effective extraction
2. Fallback: AWS Textract for complex documents
3. Cost optimization with daily spending limits
4. 99.2% document processing success rate

### Security Architecture

#### Authentication & Authorization
- **Session Management**: Redis-based session storage
- **Rate Limiting**: Tier-based API limits (Free/Pro/Enterprise)
- **Input Validation**: File type, size, and content validation
- **CORS Protection**: Configured allowed origins

#### Data Protection
- **Encryption at Rest**: S3 KMS encryption for all documents
- **Encryption in Transit**: TLS 1.3 for all connections
- **Credential Management**: Environment-based secrets
- **Redis Security**: Password authentication + TLS

#### Compliance & Auditing
- **Audit Logging**: All actions logged with correlation IDs
- **Data Retention**: 90-day document retention policy
- **PII Scrubbing**: Sensitive data anonymization
- **Request Tracking**: Distributed tracing for debugging

## Data Architecture

### Primary Database (PostgreSQL)
```sql
-- Core entities
Users              -- SME users and organizations
Sessions           -- Authentication sessions
Documents          -- LC document metadata
ValidationResults  -- Processing outcomes
BankProfiles       -- Bank-specific configurations
AuditLogs          -- Security and compliance logs
```

### Cache Layer (Redis)
```
-- Data structures
user_sessions:{user_id}     -- Session storage
rate_limit:{tier}:{user}    -- Rate limiting counters
job_status:{job_id}         -- Real-time job tracking
bank_cache:{bank_code}      -- Bank profile caching
```

### Document Storage (S3)
```
trdrhub-documents/
├── lc-originals/{job_id}/          # Uploaded documents
├── processed/{job_id}/             # OCR results
├── evidence-packs/{job_id}/        # Generated reports
└── exports/{user_id}/{date}/       # User data exports
```

## Integration Architecture

### Bank API Integration
```
Bank Profiles
├── Sonali Bank
│   ├── Document templates
│   ├── Validation rules
│   └── API endpoints
├── Dutch Bangla Bank
│   ├── Field mappings
│   ├── Format specifications
│   └── Compliance checks
└── HSBC Bangladesh
    ├── International standards
    ├── SWIFT integration
    └── Advanced validations
```

### External Service Integration
- **AWS Textract**: Advanced OCR processing
- **CloudWatch**: Monitoring and alerting
- **SES**: Email notifications
- **Lambda**: Serverless processing

## Monitoring & Observability

### Metrics Collection
```
Business Metrics:
- Document processing success rate
- Average processing time
- User engagement metrics
- Revenue per tier

Technical Metrics:
- API response times
- Error rates by endpoint
- Queue depths and processing lag
- Infrastructure costs

Security Metrics:
- Failed authentication attempts
- Rate limit violations
- Suspicious activity patterns
- Compliance violations
```

### Alerting Strategy
- **Critical**: System downtime, security breaches
- **Warning**: Performance degradation, cost overruns
- **Info**: Daily summaries, business metrics

## Scalability Design

### Current Capacity
- **Concurrent Users**: 1,000+
- **Documents/Hour**: 500+
- **Storage**: 1TB+ with intelligent tiering
- **API Throughput**: 1,000 requests/minute

### Horizontal Scaling Plan
1. **Database**: Read replicas for query offloading
2. **Application**: Multiple Flask instances behind load balancer
3. **Processing**: Auto-scaling Lambda functions
4. **Cache**: Redis cluster for high availability

## Future Architecture (Phase 5-7)

### Microservices Evolution
```
TrdrHub Platform
├── User Management Service
├── LC Validation Service
├── HS Code Intelligence Service
├── Container Tracking Service
├── Document Generation Service
├── Notification Service
└── Analytics & Reporting Service
```

### Technology Upgrades
- **Frontend**: React + TypeScript + PWA
- **API Gateway**: Kong or AWS API Gateway
- **Container Orchestration**: EKS/Fargate
- **CI/CD**: GitHub Actions + ArgoCD
- **Monitoring**: Prometheus + Grafana

### Database Strategy
- **Primary**: PostgreSQL with read replicas
- **Search**: Elasticsearch for document search
- **Analytics**: ClickHouse for business intelligence
- **Cache**: Redis Cluster for high availability

## Development Workflow

### Environment Strategy
```
Development    → Local development with mocks
Staging       → Full AWS integration for testing
Production    → Multi-AZ deployment with monitoring
```

### Deployment Pipeline
1. **Code Commit**: GitHub with branch protection
2. **Automated Testing**: Regression test suite (150+ tests)
3. **Security Scanning**: Dependency and vulnerability checks
4. **Staging Deployment**: Automated deployment for testing
5. **Production Deployment**: Manual approval with rollback capability

### Code Quality Standards
- **Python**: PEP 8, type hints, docstrings
- **Test Coverage**: 85% minimum with regression tests
- **Security**: Regular dependency updates, OWASP compliance
- **Documentation**: Comprehensive API and architecture docs

## Cost Optimization

### Current Monthly Costs (~$2,000)
- **Compute**: EC2/Lambda (~$800)
- **Storage**: S3 + EBS (~$300)
- **Database**: RDS PostgreSQL (~$400)
- **AI Services**: Textract (~$300)
- **Monitoring**: CloudWatch (~$200)

### Cost Management Strategies
- **Textract Usage**: Smart fallback with daily limits
- **S3 Storage**: Intelligent tiering and lifecycle policies
- **Lambda**: Optimized function duration and memory
- **Database**: Connection pooling and query optimization

## Security Compliance

### Standards & Frameworks
- **Data Protection**: GDPR-like principles for user data
- **Financial Compliance**: Aligned with Bangladesh Bank guidelines
- **Security Standards**: OWASP Top 10 mitigation
- **Infrastructure**: AWS Well-Architected Framework

### Regular Security Practices
- **Quarterly Security Audits**: Comprehensive vulnerability assessments
- **Monthly Dependency Updates**: Automated security patches
- **Weekly Backup Testing**: Data recovery verification
- **Daily Monitoring**: Security incident detection and response

---

**Document Version**: 2.0
**Last Updated**: September 2024
**Next Review**: December 2024

*This architecture document evolves with our platform. Each phase brings architectural improvements while maintaining backward compatibility and security standards.*