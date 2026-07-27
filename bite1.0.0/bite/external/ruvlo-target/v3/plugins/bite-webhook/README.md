# @claude-flow/bite-webhook

Bite webhook integration for Ruflo.

This plugin adds a small, native outbound webhook client so Ruflo workflows can notify Bite when proposal branches are created, code is generated, tests complete, or a deployment pipeline changes state.

## Install

```bash
npm install @claude-flow/bite-webhook
```

## Usage

```ts
import { createBiteWebhookClient } from '@claude-flow/bite-webhook';

const bite = createBiteWebhookClient({
  url: process.env.BITE_WEBHOOK_URL!,
  secret: process.env.BITE_WEBHOOK_SECRET,
  source: 'ruflo-proposals',
});

await bite.send({
  event: 'proposal.generated',
  proposalId: 'proposal_71_ruvnet-ruflo',
  branch: 'proposal/proposal_71_ruvnet-ruflo',
  repository: 'https://github.com/ruvnet/ruflo',
  metadata: {
    feature: 'bite-webhook',
    status: 'generated'
  }
});
```

## Headers

- `content-type: application/json`
- `x-bite-signature: <hex hmac sha256>` when `secret` is configured

## Suggested events

- `proposal.generated`
- `proposal.tested`
- `proposal.pushed`
- `proposal.deployed`
- `swarm.completed`

## Environment variables

- `BITE_WEBHOOK_URL`
- `BITE_WEBHOOK_SECRET`

## Notes

This package is intentionally small. It is meant to be embedded by Ruflo workflows, plugins, or proposal execution pipelines rather than forcing a single transport model on the rest of the system.