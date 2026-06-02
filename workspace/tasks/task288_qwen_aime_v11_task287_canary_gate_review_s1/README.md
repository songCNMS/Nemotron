# task288_qwen_aime_v11_task287_canary_gate_review_s1 - task287 canary gate review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=75 -->

## Background

task287 is assigned to worker_3 for the next V11 gate after #350/task285
bounded Qwen3-4B smoke evidence merged. task287 must run or block a non-AIME
canary/completion-retention check for the task285 iter2 checkpoint, without
export, endpoint, AIME/task243 eval, additional training, promotion, 30B, or
8-GPU.

The task287 acceptance branch currently exists at
`origin/intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1`
head `aa5ff7408766e44cfdb073734cff1e836c2e4e17` and contains acceptance docs
only. No task287 PR or canary artifact report is visible yet.

## Goal

Independently review task287 evidence when worker_3 provides a PR or official
mailbox report, then return `APPROVE`, `REQUEST-CHANGES`, or `BLOCK` for the
non-AIME canary gate.

## Scope

- Wait for worker_3 task287 official branch/head/PR or mailbox artifact report.
- Review the exact task287 head and artifact paths reported by worker_3.
- Verify the canary prompt source is synthetic non-AIME and not a train row.
- Verify the task285 checkpoint root, latest iteration, and checksum references
  match the approved #350/task285 evidence:
  - checkpoint root
    `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`;
  - latest iteration `2`;
  - inventory sha
    `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`;
  - checksum manifest sha
    `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`.
- Verify the canary did not use export or endpoint. If worker_3 reports that
  export or endpoint is required, review that as a `BLOCK`, not a pass.
- Verify full completion retention artifacts, checksums, and per-prompt metrics
  are sufficient for lead review.

## Boundaries

- Read-only review only.
- Do not edit code, train, run canary, run AIME/task243 eval, export, launch an
  endpoint, promote, reuse task255, use AIME2025 train prompts/labels, delete
  shared files, merge, push main, use 30B, or use 8-GPU.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1`.
- PR only if docs/status/review report files change.
- Official mailbox report with:
  - exact task287 head/PR/artifact root reviewed or exact missing-evidence
    blocker;
  - commands/checks run;
  - `APPROVE`, `REQUEST-CHANGES`, or `BLOCK`;
  - evidence summary, metrics, retained-completion artifact checksums, and
    residual risks;
  - explicit boundary confirmation.

## Acceptance Criteria

- APPROVE: task287 evidence proves an allowed no-export/no-endpoint non-AIME
  canary pass with retained coherent completions and no boundary violation.
- REQUEST-CHANGES: task287 may be valid but lacks required artifacts, hashes,
  prompt provenance, or metric clarity.
- BLOCK: task287 cannot run/load the checkpoint without export, endpoint,
  training, AIME data, task255 reuse, or another boundary violation.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related tasks: task264, task273, task285, task286, task287
- Related PRs: #350
- Gate: task287 cannot release AIME/task243 eval until this independent review
  is processed by lead.
