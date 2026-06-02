# task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1 - bounded Qwen3-4B SFT smoke

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=74 -->

## Background

Session 43 authorized a gate-driven attempt of the Qwen AIME V11 full
data-to-training-to-evaluation pipeline. The accepted packed root remains:

`/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`

task276/task277 accepted the packed artifact for the next stage while carrying
the sparse split risk: valid has one packed row and test has zero rows.

task283/#349 and task284 provide reviewed no-training runtime/config/import
evidence for the task276 packed root and Qwen3-4B path:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

task284 approved task283 only as no-training preflight evidence. It did not
clear broad training, export, endpoint, promotion, task243/AIME eval, task255
reuse, or 30B/8-GPU. Residual risks to carry into this task:

- no `AutoBridge.import_ckpt` checkpoint-load proof in task283;
- `pip check` rc `1`;
- full `nemotron.recipes.super3.stage1_sft.train` import still missing
  `nvidia_resiliency_ext`;
- `nemo.collections.llm` still missing `lightning`;
- task276 valid/test sparsity.

## Goal

Attempt the smallest bounded Qwen3-4B nonzero-LR SFT smoke on `NemTron`, fail
closed on dependency/config/checkpoint-load issues, and produce a task-owned
candidate smoke checkpoint only if the run proves it starts from real Qwen3-4B
base weights and performs a nonzero-LR optimizer step.

## Scope

- Start only after #349/task283 is merged into `main` from exact approved head
  `2d042cedb0c4cc448c89d57d7b18986d92361349`, or report if #349 cannot merge
  cleanly.
- Sync current `origin/main` to a task-owned `/root` directory on `NemTron`
  before any remote command.
- Use only Qwen3-4B:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Use only the task276 accepted packed root listed above.
- Re-run task283 fail-closed guards before any optimizer step.
- Prove real base initialization before optimizer execution by positive
  checkpoint-load evidence or Bridge-approved HF import evidence. If this proof
  is absent, stop before training and report `BLOCKED_NO_BASE_LOAD_PROOF`.
- Attempt at most a two-step smoke. The planned bounds are:
  - `train_iters=2`;
  - `global_batch_size=2`;
  - `micro_batch_size=1`;
  - `tensor_model_parallel_size=2`;
  - `pipeline_model_parallel_size=1`;
  - `seq_length=4096`;
  - `optimizer.lr=5e-7`;
  - `optimizer.min_lr=1e-7`;
  - `scheduler.lr_warmup_iters=0`;
  - `scheduler.lr_decay_iters=2`;
  - two GPUs maximum, for example `CUDA_VISIBLE_DEVICES=0,1`.
- The first logged optimizer step must show learning rate `> 0`.
- Save only task-owned smoke artifacts/checkpoints needed for review. Do not
  export or launch an endpoint.
- Treat task276 validation/test sparsity as smoke-only: loss or validation
  numbers from this task are not model-quality claims.

## Required Evidence

Report by mailbox and branch/PR if docs/status/report files change:

- branch/head/PR or exact blocker;
- exact host, shell, Python path, environment variables, package versions, GPU
  visibility, code revision, and `/root` sync path;
- exact launch command/config and all overrides, including LR, train steps,
  batch sizes, sequence length, parallelism, checkpoint/load paths, and output
  paths;
- task276 packed root, split manifest, metadata, evidence manifest, and shard
  checksum references;
- Qwen3-4B path and positive base-load/Bridge-import evidence, or exact blocker
  before training;
- proof AIME2025 prompts/labels are not trainable rows and task255 artifacts are
  not reused;
- first-step nonzero LR evidence and finite train-loss evidence if training
  starts;
- checkpoint/artifact root, checkpoint iteration, log paths, manifest, and
  checksums if a smoke checkpoint is produced;
- fail-closed evidence for zero LR, random-init-scale first loss/PPL, NaN/Inf,
  missing dependency, missing load proof, missing packed data, or shared-path
  safety issue;
- explicit boundary statement for no live canary, no AIME/task243 eval, no
  export, no endpoint, no promotion, no AIME2025 train data, no task255 reuse,
  no shared deletion, no main push, no merge by worker except an approved PR
  self-merge, and no 30B/8-GPU.

## Boundaries

- Do not run live canary, corrected AIME2025/task243 eval, export, endpoint, or
  promotion in this task.
- Do not use AIME2025 prompts or labels as trainable data. AIME2025 may only be
  used as held-out eval/decontamination material.
- Do not reuse task255 checkpoint/export/config output as a candidate or
  training source.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song` or prior task output roots.
- Do not use 30B or 8-GPU scale. This task is Qwen3-4B only and capped at two
  GPUs.
- Do not push `main` or merge without lead exact-head clearance.

## Acceptance Criteria

- PASS: a bounded Qwen3-4B smoke completes at least one and at most two
  optimizer steps from verified base-load/import proof, logs first-step LR
  `> 0`, has finite loss, writes reviewable task-owned checkpoint/artifacts,
  and preserves all boundaries.
- BLOCK: missing dependency, missing base-load/import proof, unavailable
  resource/runtime, data-contract failure, zero LR, random-init signal, NaN/Inf,
  or shared-path safety issue prevents a valid smoke.
- REQUEST-CHANGES: evidence is incomplete, stale, ambiguous, or not tied to the
  exact run artifact.

This task can only produce smoke evidence or a blocker. It does not authorize
live canary, AIME/task243 comparison, export, endpoint, promotion, or 30B/8-GPU.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task255, task260, task261, task263, task276, task277, task280,
  task283, task284
- Related PR: #349
- Current gate: bounded Qwen3-4B SFT smoke attempt after #349 merge only.
