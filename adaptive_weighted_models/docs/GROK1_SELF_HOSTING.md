# Grok-1 Self-Hosting Runbook

This path is for teams that want full control of inference and are ready for high GPU cost and ops complexity.

## Reality Check

- Grok-1 is very large and expensive to serve.
- You need multi-GPU infrastructure and careful memory planning.
- If you only need reliable production quickly, use a hosted API first.

## Recommended Architecture

1. Model serving layer:
- Use an OpenAI-compatible server runtime that supports your chosen Grok-1 checkpoint format.
- Expose endpoint like `https://YOUR-LLM-ENDPOINT/v1/chat/completions`.

2. Application layer:
- This project already supports OpenAI-compatible routing in ask flows via:
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL`

3. Internet API layer:
- Deploy this project API and set env vars to point to your self-hosted LLM endpoint.

## Minimum Deployment Steps

1. Provision GPU nodes suitable for Grok-1 serving.
2. Deploy your model server and validate `/v1/chat/completions` locally.
3. Set app environment variables:
- `OPENAI_API_KEY=<service-token>`
- `OPENAI_BASE_URL=https://YOUR-LLM-ENDPOINT`
4. Deploy this app API (Dockerfile included).
5. Validate `POST /v1/ask` end-to-end.

## Validation Checklist

- `GET /health` returns status ok.
- `POST /v1/index/build` succeeds.
- `POST /v1/search` returns ranked chunks.
- `POST /v1/ask` returns model answer from your self-hosted endpoint.

## Cost and Reliability Notes

- Add autoscaling + queueing before public traffic.
- Add request timeouts and retries at gateway.
- Add per-key rate limits and API auth for abuse protection.
- Monitor token throughput, GPU memory, and tail latency.
