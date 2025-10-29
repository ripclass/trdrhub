export interface User {
  id: string;
  email: string;
  organization: string;
  tier: 'free' | 'pro' | 'enterprise';
  quota: number;
  usage: number;
}

export interface BankProfile {
  code: string;
  name: string;
  category: 'state' | 'private' | 'islamic' | 'foreign';
  enforcementLevel: 'strict' | 'medium' | 'flexible';
  validationRules: number;
  ucpCompliance: boolean;
}

export interface ValidationRequest {
  file: File;
  bankCode: string;
  async: boolean;
  documentType?: 'lc' | 'invoice' | 'packing_list';
}

export interface ValidationResponse {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  requestId: string;
  createdAt: string;
}

export type JobStage = 'queued' | 'ocr' | 'rules' | 'evidence' | 'done';

export interface JobStatus {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  stage: JobStage;
  progress: number;
  requestId: string;
  createdAt: string;
  updatedAt: string;
  error?: ErrorResponse;
}

export interface Finding {
  id: string;
  category: string;
  severity: 'critical' | 'warning' | 'info';
  field: string;
  expected: string;
  actual: string;
  description: string;
  ucpReference?: string;
}

export interface ValidationResult {
  jobId: string;
  score: number;
  findings: Finding[];
  evidenceUrl?: string;
  evidenceSha256?: string;
  correlationId: string;
  requestId: string;
  bankProfile: BankProfile;
  processingTime: number;
  quota?: number;
  createdAt: string;
}

export interface ErrorResponse {
  error_id: string;
  type: string;
  message: string;
  details?: Record<string, any>;
  request_id?: string;
}

export interface PricingTier {
  range: string;
  pricePerCheck: number;
  currency: 'BDT';
  features: string[];
}

export interface PaymentSession {
  sessionId: string;
  redirectUrl: string;
  amount: number;
  currency: 'BDT';
}

export interface PaymentCallback {
  status: 'success' | 'failed' | 'cancelled';
  transactionId?: string;
  amount?: number;
  quota?: number;
  message?: string;
}