# task312_qwen_all_sft_independent_review_runbook_s1 - Qwen all-SFT independent review and runbook gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_4,SESSION=78 -->

## Background

The all-SFT pipeline spans inventory, packing, 30B training, canary, benchmark
evaluation, and runbook/provenance. Independent review is required before lead
closeout or any further authorization.

## Goal

Independently review task308-task311 evidence, verify boundaries and checksums,
and produce all-SFT runbook/provenance closeout with approve/request-changes/
block decision.

## Scope

- Review task308 all-SFT pipeline/data inventory.
- Review task309 packed-data contract and decontam proof.
- Review task310 training artifacts, runtime/resource evidence, checkpoint
  usability, LR/loss/validation, commands/env, and checksums.
- Review task311 canary and benchmark evidence, including base-vs-FT protocol,
  completions, parser diagnostics, unavailable benchmark rows, and residuals.
- Confirm no forbidden actions:
  - AIME2025 training prompts/labels;
  - task255 reuse;
  - shared deletion;
  - product-code edits outside assigned worker scope;
  - direct main push/merge;
  - promotion/export/endpoint claims beyond eval-only use.
- Produce runbook/provenance summary with artifact paths, code revisions,
  commands/env, metrics, blockers, residual risks, and exact gate disposition.

## Boundaries

- Read-only review and docs/status only.
- Do not train, pack, eval, export, endpoint, promote, modify product code,
  push main, merge, rewrite worker branches, reuse task255, use AIME2025 train
  data, or delete shared files.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task312_qwen_all_sft_independent_review_runbook_s1`.
- Report:
  `workspace/tasks/task312_qwen_all_sft_independent_review_runbook_s1/all_sft_independent_review_runbook_report.md`.
- Mailbox report with branch/head/PR or blocker, exact evidence reviewed,
  commands used, checksum/protocol review, metrics, unavailable benchmark rows,
  residual risks, and lead decision recommendation.

## Acceptance Criteria

- `APPROVE_CLOSEOUT`: evidence from task308-task311 is internally consistent
  and the runbook records an exact non-promotion disposition.
- `REQUEST_CHANGES`: likely valid work needs missing artifacts, checksums,
  protocol proof, runbook details, or worker closeout.
- `BLOCK`: unsafe/invalid evidence, benchmark/training failure requiring
  fail-closed closeout, or any forbidden boundary violation.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Current main: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Review targets: task308, task309, task310, task311
- Gate state: no promotion/export/endpoint/further scale decision is authorized
  by this assignment.
