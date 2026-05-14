export interface IntelligenceItem {
  id: string;
  source_type: string;
  source_name: string;
  raw_content: string;
  cleaned_content: string | null;
  risk_level: 'critical' | 'high' | 'medium' | 'low' | null;
  risk_category: string | null;
  status: 'pending' | 'processing' | 'analyzed';
  is_duplicate: boolean;
  duplicate_of_id: string | null;
  published_at: string | null;
  ingested_at: string;
  analyzed_at: string | null;
  created_at: string;
  entities?: Entity[];
  analysis_report?: AnalysisReport;
}

export interface Entity {
  id: string;
  intelligence_id: string;
  entity_type: 'slang_term' | 'link' | 'account' | 'tool' | 'phone' | 'email' | 'crypto_address';
  entity_value: string;
  entity_context: string | null;
  confidence: number;
  created_at: string;
}

export interface AnalysisReport {
  id: string;
  intelligence_id: string;
  summary: string;
  cheat_scenario: string | null;
  malicious_pattern: string | null;
  tech_chain: string | null;
  risk_score: number;
  recommendations: string | null;
  created_at: string;
}

export interface DashboardStats {
  total_items: number;
  risk_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  recent_items: IntelligenceItem[];
  critical_alerts: number;
  analyzed_count: number;
  pending_count: number;
}

export interface IntelligenceListResponse {
  items: IntelligenceItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface IntelligenceListParams {
  page?: number;
  page_size?: number;
  source_type?: string;
  risk_level?: string;
  status?: string;
  search?: string;
}

export interface IngestPayload {
  source_types?: string[];
  count?: number;
}

export interface BatchAnalyzeResponse {
  total: number;
  analyzed: number;
  skipped: number;
  errors: string[];
}

// Settings types
export interface SettingItem {
  value: string;
  description: string;
  updated_at: string | null;
}

export interface SettingsResponse {
  settings: Record<string, SettingItem>;
}

export interface LLMConfig {
  api_base: string;
  model: string;
  enabled: boolean;
}

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low';
export type IntelligenceStatus = 'pending' | 'processing' | 'analyzed';
export type EntityType = 'slang_term' | 'link' | 'account' | 'tool' | 'phone' | 'email' | 'crypto_address';