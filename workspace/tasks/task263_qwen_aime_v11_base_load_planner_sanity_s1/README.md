# task263_qwen_aime_v11_base_load_planner_sanity_s1 - V11 base-load planner sanity

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

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

- Refresh against current `origin/main` after #334/#335/#336 merge commit
  `5e839d4a911c8a0c1c55e6adc606d325b9d17717`.
- Treat #336/task262 data split/sidecar repair, #335/task264 static canary gate,
  and #334/task266 runbook gate as merged static evidence only. They do not
  authorize training, live AIME/task243 eval, promotion, or 30B/8-GPU.
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

- Do not launch full training until task263 has positive base-load/import proof
  and a later lead clearance explicitly authorizes a bounded Qwen3-4B pilot.
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
  - if blocked: exact NemTron/NeMo environment blocker, logs, missing package or
    permission, and the next smallest remediation path;
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

## Current Gate State

- #336/task262 is merged as static V11 data split/sidecar repair evidence:
  merge commit `2ca6541c275d1eb64068e665af24147a796c818a`.
- #335/task264 is merged as static non-AIME canary/retention gate evidence:
  merge commit `98e8aad39af9e705feed581e0ff9f8814073e2d8`.
- #334/task266 is merged as static runbook/repro gate evidence:
  merge commit `5e839d4a911c8a0c1c55e6adc606d325b9d17717`.
- The first V11 execution gate remains `NO-GO/HOLD` until this task proves
  Qwen3-4B base-load/import and a nonzero-LR bounded smoke plan, or reports an
  exact blocker from the NemTron/NeMo environment.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task248, task255, task258, task260, task261, task262
- First gate: explicit Qwen3-4B base-load/import proof and nonzero-LR smoke
  plan, or exact blocker.
