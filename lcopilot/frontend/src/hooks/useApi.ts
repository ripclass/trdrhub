import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = 'http://localhost:5000/api';

// Types
export interface ValidationRequest {
  files: File[];
  user_type?: 'exporter' | 'importer';
  workflow_type?: 'draft-lc-risk' | 'supplier-document-check';
}

export interface Job {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  user_type?: 'exporter' | 'importer';
  workflow_type?: string;
}

export interface ValidationResult {
  job_id: string;
  status: string;
  results: {
    overall_compliance: boolean;
    risk_score: number;
    issues: Array<{
      severity: 'low' | 'medium' | 'high' | 'critical';
      category: string;
      description: string;
      recommendation: string;
      affected_documents: string[];
    }>;
    documents: Array<{
      name: string;
      status: 'verified' | 'warning' | 'error';
      issues: string[];
    }>;
  };
}

export interface AmendmentRequest {
  job_id: string;
  selected_issues: string[];
  correction_type: 'urgent' | 'standard' | 'next_shipment';
  urgency_level: 'low' | 'medium' | 'high';
  notes?: string;
}

export interface DashboardStats {
  total_validations: number;
  successful_validations: number;
  pending_corrections: number;
  average_processing_time: string;
  recent_jobs: Job[];
}

// API Functions
const api = {
  validate: async (data: ValidationRequest): Promise<{ job_id: string }> => {
    const formData = new FormData();
    data.files.forEach(file => formData.append('files', file));
    if (data.user_type) formData.append('user_type', data.user_type);
    if (data.workflow_type) formData.append('workflow_type', data.workflow_type);

    const response = await fetch(`${API_BASE}/validate`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error('Rate limited, please retry shortly.');
      }
      throw new Error('Validation failed');
    }

    return response.json();
  },

  getJob: async (jobId: string): Promise<Job> => {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    if (!response.ok) throw new Error('Failed to fetch job');
    return response.json();
  },

  getResults: async (jobId: string): Promise<ValidationResult> => {
    const response = await fetch(`${API_BASE}/results/${jobId}`);
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
  },

  submitAmendment: async (data: AmendmentRequest): Promise<{ request_id: string }> => {
    const response = await fetch(`${API_BASE}/amendments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error('Amendment submission failed');
    return response.json();
  },

  getDashboard: async (userType: 'exporter' | 'importer'): Promise<DashboardStats> => {
    const response = await fetch(`${API_BASE}/dashboard?user_type=${userType}`);
    if (!response.ok) throw new Error('Failed to fetch dashboard');
    return response.json();
  },
};

// React Query Hooks
export const useValidate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.validate,
    onSuccess: () => {
      // Invalidate dashboard queries to refresh stats
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useJob = (jobId: string, options?: { enabled?: boolean; refetchInterval?: number }) => {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.getJob(jobId),
    enabled: options?.enabled ?? !!jobId,
    refetchInterval: (data) => {
      // Stop polling when job is completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return options?.refetchInterval ?? 2000; // Poll every 2 seconds
    },
  });
};

export const useResults = (jobId: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ['results', jobId],
    queryFn: () => api.getResults(jobId),
    enabled: options?.enabled ?? !!jobId,
  });
};

export const useAmendments = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.submitAmendment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDashboard = (userType: 'exporter' | 'importer') => {
  return useQuery({
    queryKey: ['dashboard', userType],
    queryFn: () => api.getDashboard(userType),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};