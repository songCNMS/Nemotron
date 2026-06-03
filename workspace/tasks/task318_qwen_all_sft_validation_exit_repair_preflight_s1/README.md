# task318_qwen_all_sft_validation_exit_repair_preflight_s1 - Qwen all-SFT validation/exit repair preflight

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=78 -->

## Background

Task310 reached train iter 35/35 and preserved checkpoint `iter_0000035`, but
built-in validation hung and the wrapper ended with `train_rc=1`. Task313
approved the checkpoint only for load/canary handoff. Task311 later proved the
checkpoint can load and produce mixed benchmark evidence, but no future 30B
training should repeat the same validation/exit failure mode.

## Goal

Design and verify, without training, a concrete validation/termination repair
gate for any later all-SFT 30B training attempt.

## Scope

- Review task310 launch scripts/configs/logs and the stage1 SFT training
  entrypoint for validation controls, timeout behavior, checkpoint saving,
  `train_end`/`train_rc` handling, and GPU/process teardown.
- Identify a safe route for the next training task to either:
  - complete built-in validation cleanly; or
  - explicitly skip built-in validation and hand off validation to a separate
    same-harness eval task with a clean rc and documented stop rule.
- Produce exact config keys, command fragments, timeout policy, rc policy,
  checkpoint marker policy, log evidence, and failure stop conditions.
- If a no-training import/config dry-run is possible without launching
  optimizer steps, report exact command/env and artifacts. Do not run any
  optimizer, model eval, export, endpoint, or benchmark.

## Boundaries

- No training, optimizer steps, eval rows, packing, export, endpoint, promotion,
  task255 reuse, AIME2025 train data, shared deletion, main push, merge, or
  self-merge.
- Do not modify product code. If code changes appear necessary, report the
  exact required implementation task instead of implementing it.
- Do not delete or mutate shared files under `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task318_qwen_all_sft_validation_exit_repair_preflight_s1`.
- Report:
  `workspace/tasks/task318_qwen_all_sft_validation_exit_repair_preflight_s1/validation_exit_repair_preflight_report.md`.
- Optional task-owned output root with read-only config/import probes and logs.
- Mailbox report with branch/head/PR or blocker, commands/env, exact proposed
  repair route, artifacts, stop conditions, and whether a later implementation
  task is required.

## Acceptance Criteria

- `PASS_PREFLIGHT_PLAN`: validation/exit repair route is concrete and safe for
  a later lead-gated training task.
- `REQUEST_CHANGES`: route is plausible but missing exact config, rc, timeout,
  checkpoint, or teardown proof.
- `BLOCK`: no safe validation/exit route exists without product code changes or
  unauthorized runtime action.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Inputs: task310, task313, task316
- Gate state: no training/eval authorized.
