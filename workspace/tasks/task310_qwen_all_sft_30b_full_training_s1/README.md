# task310_qwen_all_sft_30b_full_training_s1 - Qwen all-SFT 30B full training gate

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=2 -->

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
- Current main: `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`
- Product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Upstream dependencies: task308, task309, prior 30B runtime/resource evidence
- Downstream tasks: task311, task312
- Gate state: full training is HOLD until upstream evidence is accepted.

## Current Worker Disposition

Session 2 disposition: `BLOCK_PRETRAINING_GATE`.

Training was not launched because the required upstream gates are not yet
present as accepted evidence:

- task308 has a visible worker branch
  `intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1`
  at `348cba44c02043cd6310a36ec722a68278288db2`, but no PR or
  `all_sft_pipeline_inventory_audit_report.md` PASS artifact is visible.
- task309 has a visible worker branch
  `intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
  at `d054925b1792a5365738247eeb8bdec462e1e6c6`, but no PR or
  `all_sft_packed_data_contract_report.md` PASS artifact is visible.

Report:
`workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md`.
