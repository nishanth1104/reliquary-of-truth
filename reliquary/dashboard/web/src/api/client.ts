import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface RunSummary {
  work_item_id: string;
  repo_name: string;
  task_raw: string;
  ticket_title: string;
  final_status: string;
  implement_attempts: number;
  completed_at: string;
  failure_mode?: string;
}

export interface Stats {
  total_runs: number;
  successful_runs: number;
  success_rate: number;
  avg_attempts: number;
  failure_modes: Record<string, number>;
}

export const api = {
  getRuns: async (params?: { repo?: string; status?: string; limit?: number }) => {
    const response = await apiClient.get('/runs', { params });
    return response.data;
  },

  getRun: async (workItemId: string) => {
    const response = await apiClient.get(`/runs/${workItemId}`);
    return response.data;
  },

  getEvidence: async (workItemId: string) => {
    const response = await apiClient.get(`/runs/${workItemId}/evidence`);
    return response.data;
  },

  getDecisionLog: async (workItemId: string) => {
    const response = await apiClient.get(`/runs/${workItemId}/decision_log`);
    return response.data;
  },

  provideInfo: async (workItemId: string, answer: string) => {
    const response = await apiClient.post(`/runs/${workItemId}/provide_info`, { answer });
    return response.data;
  },

  approveRun: async (workItemId: string, approved: boolean, reason: string) => {
    const response = await apiClient.post(`/runs/${workItemId}/approve`, { approved, reason });
    return response.data;
  },

  getStats: async (): Promise<Stats> => {
    const response = await apiClient.get('/stats');
    return response.data;
  },
};
