---
id: T-20240228140000
title: "Set up CI pipeline"
type: infra
priority: medium
status: done
owner: "claude"
claimed_by: "claude"
labels: ["infra"]
depends_on: []
created_at: "2024-02-28T14:00:00"
updated_at: "2024-02-28T17:30:00"
---

## Context
No CI pipeline exists. PRs are merged without automated checks.
Set up GitHub Actions to run lint, tests, and build on every PR.

## Acceptance
- [x] Lint runs on every PR
- [x] Tests run on every PR
- [x] Build verified before merge
- [x] Pipeline completes in under 3 minutes

## Plan
- Write GitHub Actions workflow
- Add lint step (eslint)
- Add test step (jest)
- Add build step
- Cache node_modules for speed

## Progress Log
- created
- 2024-02-28T14:15:00 claude: claimed
- 2024-02-28T15:00:00 claude: workflow file drafted, lint and test steps working
- 2024-02-28T16:30:00 claude: build step added, caching configured
- 2024-02-28T17:30:00 claude: pipeline runs in 2m 40s, all checks green — marking done

## Handoff
Pipeline is live. All three steps (lint, test, build) run on PRs and pass.
node_modules cached via actions/cache keyed on package-lock.json hash.

## Next
- Consider adding a coverage threshold step in a follow-up task
