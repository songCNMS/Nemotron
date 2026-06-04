# task332_qwen_all_sft_structured_split_policy_remediation_s1 - Structured rows and split-policy remediation

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

task329/#392 and task330/#393 are merged as partial evidence closeout. The raw
pass expansion is still blocked by two non-SWE issues:

- `instruction-following-structured` has 6 validation-filtered rows in task329
  packing receipts.
- valid/test exposure is sparse: train exposes all three raw pass sources, but
  valid/test expose only `task322-agentic-interactive`.

These must be remediated or explicitly accepted before any expanded all-SFT
packed contract can be considered.

## Goal

Produce a no-training remediation report and task-owned evidence for the
structured filtered rows and per-source split exposure policy. The output should
state whether the raw-pass sources are ready for a later combined packed
contract after task331 SWE remediation, or fail closed with exact blockers.

## Required Inputs

- Current `origin/main`: `410c2247fc5e09e6ad831bdee1628830b97fbd89`.
- task322/#388 raw source evidence for `instruction-following-structured` and
  `agentic-interactive`.
- task329/#392 evidence root:
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.
- Merged task330/#393 review report:
  `workspace/tasks/task330_qwen_all_sft_task329_independent_review_s1/task329_independent_review_report.md`.
- Qwen3-30B model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Scope

- Branch:
  `intern_nemotron_worker_4/task332_qwen_all_sft_structured_split_policy_remediation_s1`.
- Build a task-owned output root under
  `/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/`.
- Identify the exact 6 `instruction-following-structured` filtered rows, row
  ids, validation errors, source checksums, and whether they can be fixed or
  should be excluded by a lead-visible policy.
- Define a deterministic per-source train/valid/test exposure policy for the
  raw pass sources, with minimum valid/test exposure or an exact sparse-exposure
  acceptance proposal.
- Produce intended-vs-exposed manifests and checksums. If a no-training repack
  is feasible without task331 SWE remediation, include it; otherwise state the
  exact dependency on task331.
- Preserve decontam proof and no AIME2025 prompt/label train rows.

## Expected Output

- Report:
  `workspace/tasks/task332_qwen_all_sft_structured_split_policy_remediation_s1/structured_split_policy_report.md`
- Worker branch and PR to `main` for docs/status plus any scoped helper/config
  changes.
- Mailbox closeout with:
  - branch/head/PR,
  - commands and environment,
  - output root and checksums,
  - filtered-row disposition,
  - split-policy disposition,
  - exact dependency on task331 or next combined-contract task.

## Boundaries

- No training, optimizer steps, benchmark eval, export, endpoint, promotion,
  merge, self-merge, or main push.
- No task255 reuse.
- No AIME2025 prompts or labels as training rows.
- No shared deletion or mutation, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not modify task329 artifacts in place; write task332-owned outputs.

## Acceptance Criteria

- `PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING`: structured filtered rows are
  remediated or explicitly excluded, per-source split policy is deterministic
  and evidenced, and only task331 SWE supervised-token remediation remains.
- `REQUEST_CHANGES`: evidence is incomplete, inconsistent, or missing required
  checks.
- `BLOCK_SPLIT_POLICY`: filtered rows or valid/test exposure cannot be safely
  remediated under current data/config.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Gate state: task310 training/eval/export/endpoint/promotion remain HOLD.

## Worker_4 Result

- Report:
  `workspace/tasks/task332_qwen_all_sft_structured_split_policy_remediation_s1/structured_split_policy_report.md`.
- Output root:
  `/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z`.
- Disposition: `PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING`.
- Structured row disposition:
  `PASS_STRUCTURED_ROWS_EXCLUDED_FAIL_CLOSED`.
- Split policy:
  `task332_per_source_shard_holdout_v1`, per-source `row_index % 16`
  with valid remainder `14`, test remainder `15`, train all other
  remainders.
- Residual: task331 SWE supervised-token remediation is still pending; task310
  remains HOLD.
