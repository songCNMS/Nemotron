# task323_qwen_all_sft_validation_skip_preflight_s1 - Train-only validation-skip preflight

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=78 -->

## Background

Task318 accepted a concrete validation/exit repair direction for task310's
train-loop-success but validation-hang failure. The preferred Route A is a
task-owned train-only packed root with no exposed `splits/valid/*.parquet`, so
the current training path sets `do_validation=false`, followed by a separate
same-harness eval handoff.

## Goal

Produce a no-optimizer, no-eval preflight proof for the Route A training input
and launch contract. The output should show exactly how a later training task
can avoid the task310 validation hang while preserving data/checksum/safety
proofs and an explicit same-harness eval handoff.

## Scope

- Use the currently accepted constrained task299/task310 packed root only as an
  input reference unless a later task322 materialized raw contract is accepted.
- Create a task-owned train-only/dereferenced mirror or preflight input root if
  needed; do not mutate task299 or shared roots.
- Prove train parquet/shard count, valid parquet count `0`, test exposure
  status, no symlink surprises if dereferenced, source checksums, no task255,
  no AIME2025 prompt/label train rows, and no shared deletion.
- Run no-training preflight commands only: config/root inspection, data-path
  resolution, validation auto-detection proof, and wrapper command synthesis.
- Emit the exact later launch contract fields: model path, packed root, LR/step
  placeholders, validation disposition, `do_validation=false`,
  `packed_val_data_path=null`, `same_harness_eval_handoff_required=true`, rc
  policy, checkpoint marker policy, timeout policy, and teardown proof
  requirements.

## Boundaries

- No training, optimizer steps, benchmark eval, export, endpoint, promotion,
  final packing, product-code edit, task255 reuse, AIME2025 train data, shared
  deletion, main push, merge, or self-merge.
- Do not delete or overwrite shared files under `/mnt/cephfs/data/processing/lei.song`
  or task299/task310 roots.
- If product-code changes are needed, report the implementation requirement
  instead of implementing it.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task323_qwen_all_sft_validation_skip_preflight_s1`.
- Report:
  `workspace/tasks/task323_qwen_all_sft_validation_skip_preflight_s1/validation_skip_preflight_report.md`.
- Optional task-owned output root with preflight JSON, command logs, inventory,
  and checksums.
- Mailbox report with branch/head/PR or blocker, commands/env, artifact paths,
  preflight result, and whether later training launch can be safely assigned.

## Acceptance Criteria

- `PASS_ROUTE_A_PREFLIGHT`: train-only root/preflight proves valid exposure is
  removed, `do_validation=false`, eval handoff is explicit, and later launch
  contract is concrete.
- `REQUEST_CHANGES`: route is plausible but missing root counts, validation
  proof, rc/timeout/checkpoint policy, or safety checks.
- `BLOCK`: Route A cannot be proven without product-code edits, shared
  mutation, final packing, or optimizer/eval action.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task318, task310, task313, task299
- Gate state: no training/eval authorized.
