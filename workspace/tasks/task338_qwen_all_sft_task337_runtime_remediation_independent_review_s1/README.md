# task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1 - Review task337 runtime remediation

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_4,SESSION=88 -->

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

## Acceptance

- Worker_4 acceptance mailbox:
  `intern_nemotron_worker_4-task338-accept-20260604T1042Z`.
- Worker branch:
  `origin/intern_nemotron_worker_4/task338_qwen_all_sft_task337_runtime_remediation_independent_review_s1`.
- Acceptance head: `ddbc560e244f9990b7e122c600cb12282e7d3d29`.
- Base: `origin/main` `373d162d63a66f2dac6b94c43917be9c249cd83f`.
- Lead docs imported from:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` `15dd0c0f`.
- Worker_4 accepted read-only review scope and boundaries; substantive review
  is in progress.

## Lead Gate

- Worker_4 review closeout mailbox:
  `intern_nemotron_worker_4-task338-closeout-20260604T1051Z`.
- Review PR: #401 `https://github.com/songCNMS/Nemotron/pull/401`.
- Review PR head:
  `422ca360447e083f0e08c53b446653ad44d51707`, `OPEN`, non-draft, base
  `main`, `CLEAN`/`MERGEABLE`.
- Worker_4 disposition:
  `APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE`.
- Lead verification: #401 diff scope is worker_4 status plus task338 docs/report
  only, and `git diff --check origin/main...origin/pr/401` passed.
- Lead verification of #400: exact head
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`, `OPEN`, non-draft, base
  `main`, `CLEAN`/`MERGEABLE`; diff scope is worker_2 status plus task337
  docs/report only, and `git diff --check origin/main...origin/pr/400` passed.
- Lead artifact spot-checks: task337 report sha256 matched
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`;
  `sha256sum -c manifests/artifact_checksums.sha256` passed for the assigned
  artifact root; baseline marker is
  `TASK337_IMPORT_PROBE=BLOCK_MISSING_MEGATRON_ENERGON`; final markers are
  `TASK337_IMPORT_PROBE=PASS_QWEN3_MOE_IMPORT` and
  `TASK337_SYMBOL_PROBE=PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- Decision accepted for #401:
  `APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE` as independent no-training
  runtime remediation review evidence only.
- #401 may self-merge only if exact head `422ca360` remains `OPEN`/`CLEAN`.
- #400/task337 and task310 remain HOLD until #401 lands and #400 is rechecked
  at exact head `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.

## Merge Closeout

- Worker_4 merge closeout mailbox:
  `intern_nemotron_worker_4-task338-merge-closeout-20260604T1106Z`.
- #401 merged at `2026-06-04T11:05:56Z`.
- Merge commit: `d87320cfd0f2cedb786b0588f9ee7b564c467ee1`.
- Merged head: `422ca360447e083f0e08c53b446653ad44d51707`.
- Worker_4 reported exact/CLEAN pre-merge state and no further pre-merge
  changes.
- task338 is complete as independent no-training runtime remediation review
  evidence only. #400/task337 and task310 remain HOLD pending separate #400
  recheck and lead gate.
