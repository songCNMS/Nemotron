# task263_qwen_aime_v11_base_load_planner_sanity_s1 - V11 base-load planner sanity

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_2,SESSION=4 -->

## Background

task261 found that task255 likely did not initialize from real Qwen3-4B base
weights: the retry used the raw HF directory as `SUPER3_M1_PRETRAINED_CHECKPOINT`,
logged `checkpoint.load: null`, `load_main_params_from_ckpt: false`, no positive
checkpoint-load line, random-init-scale train/valid loss, and a zero learning
rate at the only step.

## Goal

Create the V11 Qwen3-4B planner/smoke path that proves real base weight loading
or Bridge-approved HF import before SFT/export, fails closed on random-init
signals, and uses a nonzero-LR bounded pilot schedule.

## Scope

- Start from current `origin/main` after #333 merge commit
  `513fefa1f1ace94302b56413769c78fb7224624c`.
- Use Qwen3-4B only:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Identify the correct Bridge/Megatron import or checkpoint-root mechanism for
  Qwen3-4B. Do not pass a raw HF directory as a Megatron checkpoint root unless
  the loader has explicit documented support and proof.
- Add or document a fail-closed preflight requiring one of:
  - explicit `successfully loaded checkpoint ... at iteration 0` evidence; or
  - an equivalent Bridge-approved HF-import proof with logs and artifact
    manifest.
- Add or document early abort checks for missing load proof, random-init-scale
  first loss/PPL, NaN/Inf, or zero learning rate at the only step.
- Fix the pilot schedule shape so the first logged training step has nonzero LR
  and the configured iterations can consume the intended V11 split at least once.
- Prepare a bounded Qwen3-4B-only smoke launch plan for `NemTron`, including
  sync-to-`/root` path and resource shape.

## Boundaries

- Do not launch full training until task262 data readiness and lead clearance
  exist.
- Do not run task243/AIME eval, launch 30B/8-GPU, promote, or reuse task255
  checkpoint/export.
- Do not train on AIME2025 prompts or labels.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task263_qwen_aime_v11_base_load_planner_sanity_s1`.
- PR to `main` if code/config/scripts/docs change.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/`.
- Report containing:
  - branch/head/PR or blocker status;
  - exact commands/configs/scripts and environment;
  - Qwen3-4B base path and base file hashes inspected;
  - Bridge import/checkpoint-load proof or exact blocker;
  - LR/iteration schedule and why first step is nonzero LR;
  - fail-closed abort conditions;
  - NemTron sync path and resource shape if remote smoke is prepared;
  - explicit no-AIME-train-data, no AIME/task243 eval, no promotion, no
    30B/8-GPU, and no shared deletion confirmation.

## Acceptance Criteria

- PASS: a reproducible V11 base-load/import preflight exists and cannot silently
  continue from random initialization.
- PASS: the V11 pilot schedule avoids the task255 zero-LR single-step failure.
- BLOCK: exact Bridge/runtime/resource blocker is reported with logs and the
  next remediation path.
- This task does not authorize task243 comparison or promotion. Any later pilot
  checkpoint must still be judged against the accepted Qwen3-4B base `11/30`
  under the same corrected AIME harness.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task248, task255, task258, task260, task261, task262
- First gate: explicit Qwen3-4B base-load/import proof and nonzero-LR smoke
  plan, or exact blocker.

## Current Worker State

- Branch refreshed onto `origin/main`
  `5e839d4a911c8a0c1c55e6adc606d325b9d17717`.
- PR: #337
- Output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/`.
- Task-owned NemTron sync/run root:
  `/root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_20260601T234056Z`.
- Latest gate manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/manifests/v11_base_load_gate_manifest_20260601T234421Z.json`.
- Latest gate report:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/reports/task263_v11_base_load_gate_report_20260601T234421Z.md`.
- Latest artifact inventory:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/manifests/artifact_inventory_20260601T234421Z.sha256`.
- Disposition: `NEMTRON_NEMO_RUNTIME_BLOCKED`. The Bridge import proof cannot
  run in the current runtime because `megatron`/`megatron.bridge` and `nemo`
  are missing. The generated fail-closed preflight blocks before training.
- Nonzero-LR bounded smoke plan is recorded as plan-only: 1 node / 2 GPUs,
  `train_iters=2`, `global_batch_size=2`, `optimizer.lr=5e-6`,
  `scheduler.lr_warmup_iters=0`, `scheduler.lr_decay_iters=20`,
  first logged step expected LR `5e-6`; launch remains blocked until Bridge
  import/load proof, packed train rows, and lead clearance exist.
