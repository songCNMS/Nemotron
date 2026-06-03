# task310_qwen_all_sft_30b_full_training_s1 - Qwen all-SFT 30B full training gate

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=6 -->

## Background

The user requested a full pipeline on all SFT data and evaluation on available
benchmarks. The coordinator authorized an attempted gate-driven run, not a
promotion claim. The previous 30B AIME attempt failed the hard non-regression
rule: task301/task306 FT `14/30` was below task300 base `15/30`.

## Goal

Launch full Qwen3-30B-A3B all-SFT training only after data and runtime gates
pass; otherwise fail closed with exact resource/runtime/data blocker.

## Scope

- Use current `origin/main` `004870e7d790778b5cdae5cc574257fdc19ec755`
  after prerequisite merges #374, #372, and #375.
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
- If export/endpoint becomes needed, task311 must treat it as eval-only and
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
- Downstream tasks: task311, task312
- Gate state: prerequisite gates passed for the constrained V11/task299 seed
  and the bounded task310 launch was attempted.

## Current Worker Disposition

Session 6 disposition:
`TRAINING_LOOP_COMPLETE__VALIDATION_NO_LOG_PROGRESS_PENDING_LEAD_DECISION__CHECKPOINT_CANDIDATE`.

After #374/task308, #372/task309, and #375/task312 merged, task310 was refreshed
from current main and launched using only the constrained task299 packed root:
`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.

The run root is
`/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`.
The training loop reached `35/35`, saved checkpoint candidate
`/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`
(`399G`, `28` files), and logged skipped/NaN iterations `0` through iteration
35. It then entered built-in validation and had no log progress past
`Evaluating on 80 samples` / `Evaluating iter 1/10`; no `train_rc.txt` or
`train_end.txt` existed in the final Session 6 snapshot, and processes remained
alive. This is not a clean training PASS and needs lead decision for continued
wait versus termination/salvage handling.

Report:
`workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md`.
