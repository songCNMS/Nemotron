# task287_qwen_aime_v11_non_aime_canary_retention_s1 - Non-AIME canary and completion retention

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Background

PR #350/task285 merged bounded Qwen3-4B smoke evidence at merge commit
`5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0` from head
`fc379240c8517de10e37a5438f87b6b0994399f0`. The smoke produced two nonzero-LR
optimizer steps and an iter2 checkpoint, but the command returned `RC=1` only
after entering built-in validation and receiving SIGTERM. task286 approved this
as bounded smoke evidence only, not as an end-to-end training/eval pass.

The next allowed gate is a non-AIME canary/completion-retention check before any
corrected AIME2025 same-harness FT-vs-base comparison is requested.

## Goal

Run or block the non-AIME canary/completion-retention check for the task285
Qwen3-4B iter2 checkpoint, preserving enough completion evidence to determine
whether the candidate can produce coherent short final-answer responses.

## Inputs

- Base Qwen3-4B path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- task285 local output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`.
- task285 remote run root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`.
- task285 candidate checkpoint root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`.
- task285 latest checkpoint iteration: `2`.
- task285 checkpoint inventory sha:
  `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`.
- task285 checkpoint checksum manifest sha:
  `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`.
- Canary prompt source on current `origin/main`:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`.

## Scope

- Start from current `origin/main` after #350 merge commit
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`.
- Sync code to `/root` before any NemTron debug/run, per project rule.
- Use Qwen3-4B only; do not use 30B or 8-GPU scale.
- Use the task264/task273 canary/retention contract and the canary prompt set,
  but do not run AIME2025 or task243.
- Prefer a no-export, no-endpoint local checkpoint-load/generation route. If
  the only available route requires export or launching an endpoint, stop and
  report that exact blocker.
- Preserve full completion artifacts for every canary prompt, including prompt
  hash, response text, response hash, status, finish reason, extracted final
  answer, and any degeneration flags.

## Boundaries

- Do not train or run additional optimizer steps.
- Do not run AIME2025/task243 eval or use AIME2025 prompts/labels as trainable
  data.
- Do not reuse task255 artifacts.
- Do not export, launch an endpoint, promote, push main, merge, delete shared
  files, use 30B, or use 8-GPU.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- If the task285 checkpoint cannot be loaded without violating these
  boundaries, fail closed and report blocker.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1`.
- PR to `main` if docs/status/report files are added or changed.
- Task-owned local output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/`.
- Mailbox report containing:
  - branch/head/PR or exact blocker;
  - commands/env, local and NemTron paths, and source commit;
  - prompt file path and sha256, plus proof prompts are synthetic non-AIME and
    not training rows;
  - checkpoint load proof or exact checkpoint-load blocker;
  - canary result summary with per-prompt status, extracted answer, coherence
    verdict, degeneration flags, and retained completion artifact paths;
  - checksums for report, manifest, full completions, and command logs;
  - explicit confirmation of no training, no AIME/task243 eval, no export, no
    endpoint, no promotion, no task255 reuse, no shared deletion, no 30B, and no
    8-GPU.

## Worker Closeout

Worker report:
`non_aime_canary_retention_report.md`.

Disposition: `BLOCK`. The task285 iter2 checkpoint could be loaded directly
with `load_megatron_model` on one H200 without export or endpoint, but the
no-export/no-endpoint MCore generation route did not produce retained canary
completions. No AIME/task243 eval, training, export, endpoint, promotion,
task255 reuse, AIME2025 train-data use, shared deletion, 30B, or 8-GPU action
was run.

## Acceptance Criteria

- PASS: task285 iter2 checkpoint is loaded under allowed bounds, all non-AIME
  canary prompts produce retained, coherent, non-empty final-answer responses,
  and no boundary violation is observed.
- REQUEST-CHANGES: artifacts are incomplete, checksums are missing, prompt
  source/provenance is ambiguous, or completion retention is insufficient for
  review.
- BLOCK: checkpoint cannot be loaded or canary cannot run without export,
  endpoint, additional training, AIME data, task255 reuse, or other boundary
  violation.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task264, task273, task276, task283, task285, task286
- Related PRs: #344, #349, #350
- Next gate: corrected AIME2025 same-harness FT-vs-base comparison remains
  blocked until this task passes and lead explicitly releases the AIME task.
