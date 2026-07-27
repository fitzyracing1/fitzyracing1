export interface BiteWebhookPayload {
  event: string;
  source?: string;
  proposalId?: string;
  branch?: string;
  repository?: string;
  commit?: string;
  metadata?: Record<string, unknown>;
}

export interface BiteWebhookConfig {
  url: string;
  secret?: string;
  source?: string;
  timeoutMs?: number;
  defaultHeaders?: Record<string, string>;
}

export interface BiteWebhookResult {
  ok: boolean;
  status: number;
  body: string;
}