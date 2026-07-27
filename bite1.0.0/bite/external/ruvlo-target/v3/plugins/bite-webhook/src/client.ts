import { createHmac } from 'node:crypto';

import type { BiteWebhookConfig, BiteWebhookPayload, BiteWebhookResult } from './types.js';

const DEFAULT_TIMEOUT_MS = 10_000;

function buildSignature(secret: string, body: string): string {
  return createHmac('sha256', secret).update(body, 'utf8').digest('hex');
}

export class BiteWebhookClient {
  private readonly config: Required<Omit<BiteWebhookConfig, 'secret'>> & Pick<BiteWebhookConfig, 'secret'>;

  constructor(config: BiteWebhookConfig) {
    this.config = {
      url: config.url,
      secret: config.secret,
      source: config.source ?? 'ruflo',
      timeoutMs: config.timeoutMs ?? DEFAULT_TIMEOUT_MS,
      defaultHeaders: config.defaultHeaders ?? {},
    };
  }

  async send(payload: BiteWebhookPayload): Promise<BiteWebhookResult> {
    const body = JSON.stringify({
      ...payload,
      source: payload.source ?? this.config.source,
      sentAt: new Date().toISOString(),
    });

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.config.timeoutMs);

    try {
      const headers: Record<string, string> = {
        'content-type': 'application/json',
        ...this.config.defaultHeaders,
      };

      if (this.config.secret) {
        headers['x-bite-signature'] = buildSignature(this.config.secret, body);
      }

      const response = await fetch(this.config.url, {
        method: 'POST',
        headers,
        body,
        signal: controller.signal,
      });
      const responseBody = await response.text();

      return {
        ok: response.ok,
        status: response.status,
        body: responseBody,
      };
    } finally {
      clearTimeout(timeout);
    }
  }
}

export function createBiteWebhookClient(config: BiteWebhookConfig): BiteWebhookClient {
  return new BiteWebhookClient(config);
}