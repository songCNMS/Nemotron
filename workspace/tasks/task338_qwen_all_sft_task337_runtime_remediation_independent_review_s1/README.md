# task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1 - Review task337 runtime remediation

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=88 -->

## Background

task337/#400 reports `PASS_RUNTIME_REMEDIATED` for the missing
`megatron.energon` blocker that stopped task335/#398. The claimed fix is
task-owned only: packages are installed into a task-owned NemTron runtime target
and prepended on `PYTHONPATH`; no system/user-site/shared-root mutation should
have occurred.

This is a runtime gate before any task335-equivalent no-training preflight rerun
can be assigned, so #400 requires independent read-only review.

## Review Target

- PR: #400 `https://github.com/songCNMS/Nemotron/pull/400`
- Exact head: `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`
- Base: `main`
- Observed PR state: `OPEN`, non-draft, `CLEAN`/`MERGEABLE`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z`
- Remote artifact root:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z`
- Runtime target:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`
- Report:
  `workspace/tasks/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/qwen3_moe_runtime_remediation_report.md`
- Report sha256:
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`

## Goal

Return one of:

- `APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE`: #400 accurately documents a
  task-owned no-training runtime import remediation. This does not release
  training.
- `REQUEST_CHANGES`: report/artifacts are incomplete, inconsistent, or missing
  required proof.
- `BLOCK_REVIEW`: evidence is unsafe, ambiguous, or cannot be reviewed without
  unauthorized runtime/training action.

## Required Checks

- PR metadata: exact #400 head
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`, base `main`, non-draft,
  clean/mergeable, no material head drift.
- Diff scope: worker_2 status plus task337 README/history/task_knowledge/report
  only; no product/source code changes.
- `git diff --check origin/main...origin/intern_nemotron_worker_2/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1`.
- Validate task337 artifact checksums from the assigned local run root:
  `sha256sum -c manifests/artifact_checksums.sha256`.
- Confirm report sha256 equals
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.
- Confirm baseline reproduces `BLOCK_MISSING_MEGATRON_ENERGON`.
- Confirm final import probe reports `TASK337_IMPORT_PROBE=PASS_QWEN3_MOE_IMPORT`.
- Confirm symbol probe reports `TASK337_SYMBOL_PROBE=PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- Confirm remediation packages are only in the task-owned runtime target and
  wheel/cache manifests are present with checksums.
- Confirm boundaries: no model construction, weight load, training, optimizer
  step, eval, export, endpoint, promotion, task310 release, task255 reuse,
  AIME2025 train rows, shared-root mutation/deletion, main push, merge, or
  self-merge.
- State residual risk and next gate: a task335-equivalent no-training launch
  preflight rerun is still required before any training task.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1`.
- Report:
  `workspace/tasks/task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1/task337_runtime_remediation_independent_review_report.md`.
- Mailbox closeout with branch/head/PR, commands run, pass/fail findings,
  residuals, and exact decision for #400.

## Boundaries

- Read-only review only.
- Do not modify task337 artifacts or worker_2 branch.
- Do not install packages, mutate runtime, run training, optimizer steps, eval,
  export, endpoint, promotion, task310, task255, AIME2025 train rows, shared
  deletion/mutation, main push, merge, or self-merge.
- If more runtime action appears needed, report the exact follow-up task;
  do not perform it.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Base: current `origin/main` `373d162d63a66f2dac6b94c43917be9c249cd83f`
- Gate state: #400/task337 and task310 remain HOLD pending this review.

## Worker_4 Acceptance

- Accepted: `2026-06-04T10:41:39Z`
- Branch:
  `intern_nemotron_worker_4/task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1`
- Acceptance scope: independent read-only review of #400 exact head
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091` and assigned artifact root.
- Boundary confirmation: no task337 artifact or worker_2 branch mutation; no
  package install, runtime mutation, training, eval, export, endpoint,
  promotion, task310/task255, AIME2025 train rows, shared deletion, main push,
  merge, or self-merge.

## Worker_4 Review Result

- Report:
  `workspace/tasks/task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1/task337_runtime_remediation_independent_review_report.md`
- Reviewed #400 exact head:
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`
- Disposition: `APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE`
- Summary: #400 accurately documents task-owned no-training runtime import
  remediation. Baseline reproduces missing `megatron.energon`; final
  task-owned `PYTHONPATH` route passes `megatron.energon` and
  `megatron.bridge.recipes.qwen.qwen3_moe` import plus qwen3_moe symbol probe.
  This remains evidence only and task310/30B launch stay HOLD pending a later
  task335-equivalent no-training preflight rerun.
