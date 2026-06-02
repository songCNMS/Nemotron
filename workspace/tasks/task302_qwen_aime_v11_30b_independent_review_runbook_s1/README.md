# task302_qwen_aime_v11_30b_independent_review_runbook_s1 - 30B independent review and runbook

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=76 -->

## Background

The 30B Qwen AIME V11 workflow needs independent review and persistent
runbook/provenance before any lead gate can accept training/testing results.

## Goal

Independently review task298-task301 evidence and maintain a 30B runbook matrix
with exact artifacts, commands, metrics, residuals, and gate disposition.

## Scope

- Track task298 runtime/base-load, task299 data/packing, task300 testing, and
  task301 training branches/PRs/artifacts.
- Review exact heads and artifact roots when they are available.
- Verify file scopes, command/env logs, checksums, gate sequencing, no AIME2025
  train rows, no task255 reuse, and no shared deletion.
- Record final 30B gate disposition only after task300 reports same-harness
  FT-vs-base metrics.
- Do not run training/testing personally unless lead later assigns a specific
  read-only review command; default is independent review and runbook.

## Boundaries

- No product code edits, training, AIME scoring, canary run, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, shared deletion, main push,
  merge, or release/scale claim.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task302_qwen_aime_v11_30b_independent_review_runbook_s1`
- Report/runbook:
  `workspace/tasks/task302_qwen_aime_v11_30b_independent_review_runbook_s1/30b_independent_review_runbook.md`
- Mailbox reports with exact reviewed heads/artifacts, approve/request-changes/
  block decisions per gate, residual risks, and final no-promotion boundary.

## Acceptance Criteria

- APPROVE: evidence is complete, gate order is preserved, metrics are
  independently consistent, artifacts/checksums are reviewable, and no
  forbidden action appears.
- REQUEST-CHANGES: missing PR heads, artifact paths, commands/env, checksums,
  metrics, or residuals.
- BLOCK: gate order violated, contamination/task255/shared deletion risk, FT
  below base, or unreviewable artifacts.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Current main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Related tasks: task298, task299, task300, task301
