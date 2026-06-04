# task335_qwen_all_sft_task333_30b_launch_preflight_s1 - Qwen all-SFT task333 30B launch preflight

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=88 -->

## Background

#396/task333 merged the combined all-SFT packed-contract evidence into
`origin/main` at `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`. The user asked to
advance the all-SFT data -> training -> benchmark pipeline, but task310
training/eval remains HOLD until the current-main launch contract is proven
fail-closed.

The previous task310 run produced a salvage candidate, not `PASS_TRAINING`,
because built-in validation hung and wrapper rc was nonzero. This task must
preflight the next 30B launch route before any optimizer step is allowed.

## Goal

Produce a no-training Qwen3-30B all-SFT launch/config/import/resource preflight
for the merged task333 packed root. The output must say whether a later
lead-gated training task can be safely assigned, or exactly why it must remain
blocked.

## Inputs

- Current main:
  `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`.
- Model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- task333 artifact root:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`.
- task333 packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`.
- task323 validation-skip route, task318 validation/exit repair plan, task310
  validation-hang evidence, and task334 independent review.

## Required Checks

- Sync current main to the required remote/debug location before any remote
  preflight. Follow project rule: code/debug runs happen on `NemTron`, code must
  be synced to `/root` before debug.
- Confirm the 30B model path exists and identify exact tokenizer/chat-template
  assumptions.
- Confirm task333 packed root exists, resolves safely, has train/valid/test
  split visibility understood, and does not require mutating shared roots.
- Decide whether the later training launch should use the full packed root or a
  task-owned train-only view to preserve task323 `do_validation=false` route.
- Synthesize the exact later launch contract:
  model path, packed train path, validation disposition, LR placeholder, steps
  placeholder, global batch/sequence/precision, tensor/pipeline/context/data
  parallelism, host/GPU count, output root, checkpoint policy, timeout policy,
  rc policy, teardown policy, and same-harness eval handoff.
- Run only no-training preflight/import/config checks. Acceptable checks include
  import/symbol checks, config rendering, data-path resolution, dry command
  construction, and fail-closed validation auto-detection proof.
- Report whether a later implementation/training task is needed, and what exact
  command/env it should use if released.

## Boundaries

- No training, optimizer steps, benchmark eval, AIME/task243 eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
  main push, merge, or self-merge.
- Do not delete or mutate files under `/mnt/cephfs/data/processing/lei.song` or
  any shared model/data roots.
- Do not silently downgrade to 4B or switch Qwen checkpoint paths.
- If the preflight requires product-code edits, container credentials, missing
  runtime packages, unavailable GPUs, or a destructive data operation, return
  `BLOCK` with exact evidence instead of working around it.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task335_qwen_all_sft_task333_30b_launch_preflight_s1`.
- Report:
  `workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/task333_30b_launch_preflight_report.md`.
- Optional task-owned output root with configs, dry-run logs, manifests, and
  checksums.
- Mailbox closeout with branch/head/PR or blocker, commands/env, remote paths,
  artifact paths, pass/fail disposition, and exact next training-task release
  recommendation.

## Acceptance Criteria

- `PASS_LAUNCH_PREFLIGHT`: current-main task333 30B launch contract is concrete,
  no-training checks pass, validation/exit route is safe, and a later
  lead-gated training task can be assigned with exact command/env.
- `REQUEST_CHANGES`: preflight is plausible but missing exact config, resource,
  validation, checkpoint, timeout, rc, path, or artifact evidence.
- `BLOCK_LAUNCH_PREFLIGHT`: runtime/resource/config/data gates fail, route would
  repeat task310 validation hang without a safe exit, or the launch would require
  unauthorized training/eval/shared mutation/downgrade/product-code change.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Base: current `origin/main` `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`
- Gate state: task310/training/eval/export/endpoint/promotion/30B release remain
  HOLD pending this no-training preflight and later lead gate.

## Lead Gate

- #398 exact head approved for worker_2 self-merge:
  `0a094483458f01813b50e4fb13e2ddefdbdc4517`.
- Gate basis: worker_2 task335 closeout plus merged task336/#399 independent
  review evidence.
- Final post-#399 state: #398 `OPEN`, non-draft, base `main`,
  `CLEAN`/`MERGEABLE`.
- Decision: `APPROVE_TASK335_BLOCKER_DOCS_CLOSEOUT`.
- Meaning: accept #398 as no-training fail-closed preflight/blocker evidence
  only.
- Still blocked: task310/all-SFT 30B launch/training/eval/export/endpoint/
  promotion. Next allowed lead action after #398 lands is a bounded runtime
  remediation task for missing `megatron.energon` or equivalent NemTron route
  fix, followed by a rerun no-training preflight.

## Merge Closeout

- #398 merged at `2026-06-04T09:45:30Z`.
- Merge commit: `373d162d63a66f2dac6b94c43917be9c249cd83f`.
- Merged evidence head: `0a094483458f01813b50e4fb13e2ddefdbdc4517`.
- Worker_2 branch-only closeout head:
  `dad0fa87a196b75ec51fbfc9d317f9c402aaeb15`.
- task335 is complete as no-training fail-closed blocker documentation only.
- task310/all-SFT 30B launch/training/eval/export/endpoint/promotion remain
  HOLD pending separate runtime remediation and no-training preflight.
