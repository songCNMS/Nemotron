# task289_qwen_aime_v11_post_smoke_runbook_provenance_s1 - Post-smoke runbook provenance

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=75 -->

## Background

The V11 Qwen AIME pipeline has advanced past packed data, no-training
preflight, and bounded Qwen3-4B smoke. PR #350/task285 merged bounded smoke
evidence at merge commit `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`. The next
gate is task287 non-AIME canary/completion retention, currently assigned and
not yet complete.

Runbook/provenance must reflect this state without implying AIME eval,
promotion, export, endpoint, 30B, or 8-GPU clearance.

## Goal

Update or report runbook/provenance state for the post-smoke V11 pipeline:
#350/task285 merged evidence, task286 approval, task287 current gate, task288
review gate, and the remaining corrected AIME2025 FT-vs-base requirement.

## Scope

- Start from current `origin/main` after #350 merge commit
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`.
- Reconcile these facts:
  - #344/task276 packed_qwen evidence merged, with sparse valid/test risk;
  - #349/task283 no-training preflight merged;
  - #350/task285 bounded smoke evidence merged;
  - task286 approved #350 as smoke evidence only;
  - task287 is active for non-AIME canary/completion retention;
  - task288 is the independent review gate for task287.
- Preserve accepted base comparator for later AIME:
  Qwen3-4B base score `11/30 = 0.36666666666666664` under the corrected
  AIME2025 harness.
- Make clear that same-harness FT-vs-base AIME comparison remains blocked until
  task287 passes and lead explicitly releases the AIME task.

## Boundaries

- Do not run training, canary, AIME/task243 eval, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, merge, push main, 30B, or
  8-GPU.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task289_qwen_aime_v11_post_smoke_runbook_provenance_s1`.
- PR to `main` if runbook/docs/status files change.
- Mailbox report with:
  - branch/head/PR or exact blocker;
  - changed files and summary;
  - provenance matrix of task276/task283/task285/task286/task287/task288;
  - artifact paths and metrics carried forward;
  - explicit no-clearance statement for AIME/task243, export, endpoint,
    promotion, 30B, and 8-GPU.

## Acceptance Criteria

- PASS: runbook/provenance accurately captures current V11 gate state and does
  not overstate clearance.
- REQUEST-CHANGES: stale head/PR/artifact metadata or ambiguous next gate.
- BLOCK: required provenance cannot be found from repo or lead docs.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related tasks: task276, task277, task283, task284, task285, task286, task287,
  task288
- Related PRs: #344, #349, #350
