---
id: T-20240301090000
title: "Add rate limiting to the API"
type: feature
priority: high
status: backlog
owner: ""
labels: ["backend", "infra"]
depends_on: []
created_at: "2024-03-01T09:00:00"
updated_at: "2024-03-01T09:00:00"
---

## Context
The public API has no rate limiting. Under load tests, a single client can saturate the server.
Limit each API key to 100 req/min using a sliding window counter stored in Redis.

## Acceptance
- [ ] Requests exceeding the limit return 429 with a Retry-After header
- [ ] Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining) present on every response
- [ ] Limits configurable per API key tier

## Plan
- Add Redis sliding window middleware
- Wire middleware into the Express router
- Expose config via environment variables
- Write integration tests for limit and recovery behavior

## Progress Log
- created

## Handoff


## Next
- Claim and implement Redis middleware
