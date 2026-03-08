---
id: T-20240302110000
title: "Migrate auth service to JWT"
type: feature
priority: high
status: in_progress
owner: "claude"
claimed_by: "claude"
claimed_until: "2024-03-02T13:00:00"
labels: ["backend"]
depends_on: []
created_at: "2024-03-02T09:00:00"
updated_at: "2024-03-02T11:45:00"
---

## Context
The current session-based auth does not scale horizontally. Migrate to stateless JWT tokens
so any instance can verify requests without hitting the session store.

## Acceptance
- [ ] Login endpoint returns signed JWT (access + refresh tokens)
- [ ] Middleware verifies JWT on protected routes
- [ ] Refresh token rotation implemented
- [ ] Old session-based code removed

## Plan
- Implement JWT sign/verify helpers
- Replace session middleware with JWT middleware
- Update login and logout endpoints
- Add refresh token endpoint
- Remove session store dependency

## Progress Log
- created
- 2024-03-02T09:15:00 claude: claimed
- 2024-03-02T10:30:00 claude: JWT sign/verify helpers done, tests passing
- 2024-03-02T11:45:00 claude: login endpoint updated, returns access + refresh tokens

## Handoff
Login and token generation are working. Middleware verification and refresh rotation still needed.
Session store is still wired — do not remove it until the middleware is fully replaced.

## Next
- Implement JWT verification middleware for protected routes
- Add POST /auth/refresh endpoint with token rotation
- Remove session store after middleware is confirmed working
