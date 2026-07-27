/**
 * @claude-flow/bite-webhook
 *
 * Native Bite webhook integration for Ruflo/Claude Flow.
 * Provides a small outbound event client so swarms, proposal executors,
 * and custom plugins can notify Bite about repository, branch, and deployment events.
 */

export { BiteWebhookClient, createBiteWebhookClient } from './client.js';
export type { BiteWebhookConfig, BiteWebhookPayload, BiteWebhookResult } from './types.js';

import { createBiteWebhookClient } from './client.js';
export default createBiteWebhookClient;