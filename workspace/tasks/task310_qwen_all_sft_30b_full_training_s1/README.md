# task310_qwen_all_sft_30b_full_training_s1 - Qwen all-SFT 30B full training gate

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=78 -->

## Background

The user requested a full pipeline on all SFT data and evaluation on available
benchmarks. The coordinator authorized an attempted gate-driven run, not a
promotion claim. The previous 30B AIME attempt failed the hard non-regression
rule: task301/task306 FT `14/30` was below task300 base `15/30`.

## Goal

Launch full Qwen3-30B-A3B all-SFT training only after data and runtime gates
pass; otherwise fail closed with exact resource/runtime/data blocker.

## Scope

- Use current `origin/main` `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`.
  Lead verified this is a docs-only task310 task-doc advance from product-code
  baseline `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- Prioritize target model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Before training, verify:
  - task308 `PASS_AUDIT`;
  - task309 `PASS_PACKED_CONTRACT`;
  - current 30B runtime/resource route is still valid or explicitly refreshed
    from task298/task300/task301/task306 evidence;
  - exact GPUs, host, parallelism, launch entrypoint, config, output roots, and
    checkpoint policy.
- If a required gate is missing, return `BLOCK_PRETRAINING_GATE` or a more
  specific blocker; do not silently downgrade to 4B or a different Qwen path.
- When gates pass, run full all-SFT training and record:
  - command/env;
  - model path and tokenizer;
  - packed root and source manifest;
  - LR, optimizer, train steps, schedule, seed, precision, parallelism;
  - loss and validation summaries;
  - checkpoint paths and checksum manifests;
  - resource usage and failure/retry notes;
  - handoff for task311 canary/benchmark eval.

## Boundaries

- No AIME2025 prompts or labels in training data.
- No task255 reuse.
- No shared deletion under `/mnt/cephfs/data/processing/lei.song`.
- No export, endpoint, promotion, direct main push, merge, or product-code
  modification.
- If export/endpoint is later needed, task311 must treat it as eval-only and
  document it separately.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task310_qwen_all_sft_30b_full_training_s1`.
- Report:
  `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md`.
- Remote training root and local evidence root with launch scripts/configs,
  logs, loss/validation summaries, checkpoint manifests, checksums, and task311
  handoff.
- Mailbox report with branch/head/PR or blocker, upstream gate references,
  exact commands/env, GPU/resource evidence, checkpoint paths, metrics, and
  residual risks.

## Acceptance Criteria

- `PASS_TRAINING`: required gates passed, training completed with a usable
  Qwen3-30B-A3B all-SFT checkpoint, finite loss/validation evidence, complete
  commands/env/logs/checksums, and task311 handoff.
- `REQUEST_CHANGES`: report/artifacts lack required config, metrics, checksums,
  validation, or handoff evidence.
- `BLOCK`: data/runtime/resource gates are absent, launch fails without usable
  checkpoint, contamination risk appears, shared deletion would be needed, or
  the run would require unauthorized downgrade/promotion/export.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Current main: `004870e7d790778b5cdae5cc574257fdc19ec755`
- Product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Upstream dependencies: task308, task309, prior 30B runtime/resource evidence
- Downstream tasks: task311, task312, task313
- Gate state: final checkpoint is a salvage candidate only. Task311 remains
  HOLD until task313 independent review is accepted by lead.

## Current Lead Disposition

Worker_5 refreshed PR #373 to final salvage evidence head
`7561a578f5f624cf1d3b85bef0dd8abb5c787533` and reported
`TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`.
After the lead HOLD notice, #373 advanced to
`0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8` with worker_5 status plus task310
history/task_knowledge bookkeeping only; the training report content is
expected to remain unchanged pending task313 verification.

The bounded run reached training iter `35/35`, recorded finite training losses,
and preserved checkpoint candidate
`/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`
(`399G`, `28` files; payload manifest sha256
`8cb4e7856f379bc7f1d63d407582bd63981b61c9f346455aa40fb389ef73cbe8`).
Built-in validation did not complete, the lead-cleared salvage sent SIGTERM to
the task310 torchrun parent, and the wrapper wrote `train_rc.txt=1`.

This is not `PASS_TRAINING`. #373 remains HOLD pending task313 independent
review; no task311 checkpoint-load/canary/benchmark, AIME/task243 eval, export,
endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
direct main push, merge, or product-code edit is authorized by this state.
