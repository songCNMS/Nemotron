# task336_qwen_all_sft_task335_independent_review_s1 - Review task335 launch preflight

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

task335/#398 produced a no-training current-main Qwen3-30B all-SFT launch
preflight for the accepted task333 packed root. The reported disposition is
`BLOCK_LAUNCH_PREFLIGHT / BLOCK_RUNTIME_MISSING_IMPORT`: data, model, resource,
Qwen contract, and validation-route checks pass, but the NemTron runtime cannot
import the Qwen3 MoE Bridge recipe because `megatron.energon` is missing.

This is a critical gate before any task310/all-SFT 30B training launch, so #398
requires independent read-only review before lead accepts the docs closeout or
creates a runtime remediation task.

## Review Target

- PR: #398 `https://github.com/songCNMS/Nemotron/pull/398`
- Exact head: `0a094483458f01813b50e4fb13e2ddefdbdc4517`
- Base: `main`
- Observed PR state: `OPEN`, non-draft, `CLEAN`/`MERGEABLE`
- Local evidence root:
  `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z`
- Remote evidence root:
  `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z`
- Report:
  `workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/task333_30b_launch_preflight_report.md`

## Goal

Return one of:

- `APPROVE_TASK335_BLOCKER_DOCS_CLOSEOUT`: #398 accurately documents a
  no-training fail-closed launch preflight and should be accepted as blocker
  evidence. This does not release training.
- `REQUEST_CHANGES`: report/artifacts are incomplete, inconsistent, or missing
  checks needed to support the blocker.
- `BLOCK_REVIEW`: the evidence is unsafe, ambiguous, or cannot be reviewed
  without unauthorized runtime/training action.

## Required Checks

- PR metadata: exact #398 head
  `0a094483458f01813b50e4fb13e2ddefdbdc4517`, base `main`, non-draft,
  clean/mergeable, no material head drift.
- Diff scope: worker_2 status plus task335 README/history/task_knowledge,
  task-local helper, and task335 report only.
- `git diff --check origin/main...origin/intern_nemotron_worker_2/task335_qwen_all_sft_task333_30b_launch_preflight_s1`.
- Helper compile:
  `python3 -m py_compile workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/build_task335_30b_launch_preflight.py`.
- Artifact checksum validation from the task335 run root:
  `sha256sum -c manifests/artifact_checksums.sha256`.
- Train-only shard checksum validation:
  `sha256sum -c manifests/train_only_shard_checksums.sha256`.
- Confirm final summary disposition `BLOCK_LAUNCH_PREFLIGHT` and remote probe
  disposition `BLOCK_RUNTIME_MISSING_IMPORT`.
- Confirm pass subchecks:
  model path exists as Qwen3 MoE with tokenizer chat template, task-owned
  train-only view has 84 train shards and 0 valid/test shards, Qwen packed
  contract passes, validation route resolves to `do_validation=false`, and 8 H200
  GPUs are visible.
- Confirm exact blocker:
  `megatron.bridge.recipes.qwen.qwen3_moe` fails with
  `ModuleNotFoundError("No module named 'megatron.energon'")`, while base imports
  such as `megatron`, `megatron.bridge`, `megatron.bridge.training.config`,
  `torch`, `omegaconf`, and task-local Qwen code pass.
- Confirm boundaries: no optimizer/training/eval/export/endpoint/promotion/30B
  release/task310/task255/AIME2025 train rows/shared deletion/main push/merge/
  self-merge.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task336_qwen_all_sft_task335_independent_review_s1`.
- Report:
  `workspace/tasks/task336_qwen_all_sft_task335_independent_review_s1/task335_independent_review_report.md`.
- Mailbox closeout with branch/head/PR, commands run, pass/fail findings,
  residuals, and exact decision for #398.

## Boundaries

- Read-only review only.
- Do not modify task335 artifacts or worker_2 branch.
- Do not run training, optimizer steps, eval rows, export, endpoint, promotion,
  task310 release, task255, AIME2025 train rows, shared deletion/mutation, main
  push, merge, or self-merge.
- If the blocker appears fixable by installing packages or mutating the runtime,
  report the exact remediation task needed; do not perform it.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Base: current `origin/main` `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`
- Gate state: #398 and task310 remain HOLD pending this review.
