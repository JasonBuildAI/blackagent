import axios, { AxiosError } from 'axios';
import type {
  DashboardStats,
  IntelligenceListResponse,
  IntelligenceListParams,
  IntelligenceItem,
  AnalysisReport,
  IngestPayload,
  BatchAnalyzeResponse,
  SettingsResponse,
  LLMConfig,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as Record<string, unknown>;
      const message = (data?.detail as string) || `请求失败 (${status})`;
      console.error(`API Error [${status}]:`, message);
      throw new Error(message);
    } else if (error.request) {
      console.error('Network Error:', error.message);
      throw new Error('网络连接失败，请检查后端服务是否启动');
    }
    throw error;
  }
);

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>('/intelligence/stats');
  return response.data;
}

export async function getIntelligenceList(
  params: IntelligenceListParams = {}
): Promise<IntelligenceListResponse> {
  const response = await apiClient.get<IntelligenceListResponse>('/intelligence', {
    params: {
      page: params.page || 1,
      page_size: params.page_size || 20,
      ...(params.source_type && { source_type: params.source_type }),
      ...(params.risk_level && { risk_level: params.risk_level }),
      ...(params.status && { status: params.status }),
      ...(params.search && { search: params.search }),
    },
  });
  return response.data;
}

export async function getIntelligenceDetail(id: string): Promise<IntelligenceItem> {
  const response = await apiClient.get<IntelligenceItem>(`/intelligence/${id}`);
  return response.data;
}

export async function ingestData(payload: IngestPayload): Promise<{ total_generated: number; new_items: number; duplicates: number; message: string }> {
  const response = await apiClient.post<{ total_generated: number; new_items: number; duplicates: number; message: string }>('/intelligence/ingest', payload);
  return response.data;
}

export async function analyzeIntelligence(id: string): Promise<AnalysisReport> {
  const response = await apiClient.post<AnalysisReport>(`/analysis/${id}`);
  return response.data;
}

export async function batchAnalyze(ids: string[]): Promise<BatchAnalyzeResponse> {
  const response = await apiClient.post<BatchAnalyzeResponse>('/analysis/batch', { intelligence_ids: ids });
  return response.data;
}

export async function getAnalysisReport(intelligenceId: string): Promise<AnalysisReport> {
  const response = await apiClient.get<AnalysisReport>(`/analysis/${intelligenceId}`);
  return response.data;
}

export async function deleteIntelligence(id: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(`/intelligence/${id}`);
  return response.data;
}

// Settings API
export async function getSettings(): Promise<SettingsResponse> {
  const response = await apiClient.get<SettingsResponse>('/settings');
  return response.data;
}

export async function getLLMConfig(): Promise<LLMConfig> {
  const response = await apiClient.get<LLMConfig>('/settings/llm');
  return response.data;
}

export async function updateSetting(key: string, value: string): Promise<{ key: string; value: string; description: string; updated_at: string | null }> {
  const response = await apiClient.put(`/settings/${key}`, { value });
  return response.data;
}

export async function testLLMConnection(): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post('/settings/llm/test');
  return response.data;
}

export default apiClient;