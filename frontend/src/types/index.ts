export interface KpiData {
  id: string;
  name: string;
  module: "FI" | "SD" | "MM" | "PP";
  value: number;
  unit: string;
  trend: number[];
  status: "green" | "amber" | "red";
  threshold_amber: number;
  threshold_red: number;
  description: string;
  higher_is_better: boolean;
}

export interface Cause {
  title: string;
  description: string;
  severity: "high" | "medium" | "low";
  affected_records: number;
  recommendation: string;
}

export interface RcaEvent {
  date: string;
  event: string;
  impact: string;
}

export interface RcaData {
  summary: string;
  causes: Cause[];
  timeline: RcaEvent[];
}

export interface RcaResponse {
  kpi_id: string;
  rca: RcaData;
}

export interface ProcessNode {
  id: string;
  label: string;
  frequency: number;
  type: "start" | "end" | "activity";
}

export interface ProcessEdge {
  id: string;
  source: string;
  target: string;
  frequency: number;
  label: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string | null;
  sql?: string;
  columns?: string[];
  chart_config?: any;
  data?: any[];
  execution_time_ms?: number;
  row_count?: number;
  from_cache?: boolean;
}

export interface MiningSourceResponse {
  source: string;
  label: string;
}

export interface MiningDiscoverResponse {
  task_id: string;
  status: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
  result?: {
    nodes: ProcessNode[];
    edges: ProcessEdge[];
    bottlenecks?: Array<Record<string, any>>;
  };
}
