# task291_qwen_aime_v11_no_export_canary_route_unblock_s1 - No-export canary route unblock

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Background

task287 officially blocks the V11 non-AIME canary gate. PR #352 reports that
the task285 iter2 checkpoint can be loaded on one H200, but the allowed
no-export/no-endpoint in-process MCore generation route cannot produce retained
non-AIME canary completions.

task288 approved task287 closeout as `BLOCK` evidence. task290 independently
approved the same blocker closeout and recommended a bounded unblock task for
the local generation route.

## Goal

Repair or prove a no-export/no-endpoint local generation path for the task285
Qwen3-4B iter2 checkpoint, then rerun the synthetic non-AIME canary prompt set
with retained completion artifacts. If the route cannot be repaired within the
task boundaries, report a precise blocker.

## Inputs

- Current base: `origin/main` after #350 merge
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`.
- task287 PR #352 current approved blocker head:
  `52834d74c79ab98b5e125434160843752c34d47a`.
- task285 checkpoint root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`.
- task285 checkpoint iteration:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`.
- Base Qwen3-4B path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Canary prompt source:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`.
- task287 output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`.

## Known Blockers To Address

- `20260602T071900Z`: `ImportError: cannot import name 'get_model_config' from
  'megatron.core.transformer.module'`.
- `20260602T072300Z`: `ValueError: Unknown attention backend None` after
  reaching `GPTInferenceWrapper`.
- `20260602T072800Z`: `torch.AcceleratorError: CUDA error: device-side assert
  triggered` during sampling after in-memory `AttnBackend.auto` adjustment.
- Runtime probes also noted missing `megatron.core.inference.text_generation`,
  missing `megatron.energon` for `megatron.bridge.recipes.qwen`, and missing
  `nvidia_resiliency_ext` for some training imports. Do not install or change
  dependencies unless strictly needed for the allowed no-export/no-endpoint
  inference route and fully documented.

## Scope

- Start from current `origin/main`.
- Create worker branch:
  `intern_nemotron_worker_2/task291_qwen_aime_v11_no_export_canary_route_unblock_s1`.
- Sync code to `/root` before NemTron debug/run, per project rule.
- Use Qwen3-4B only and at most one visible GPU.
- May make narrowly scoped code/script/config changes needed to support a
  no-export/no-endpoint in-process local generation route for the task285 iter2
  Megatron torch-dist checkpoint.
- May run no-training local inference/canary probes on the five synthetic
  non-AIME prompts only.
- Must retain completion artifacts if any generation succeeds:
  `canary_summary.json`, `canary_results.jsonl`,
  `canary_full_completions.jsonl`, command/env logs, prompt manifest,
  checkpoint-load manifest, and checksum manifest.

## Boundaries

- Do not train or run additional optimizer steps.
- Do not run AIME2025/task243 eval.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not reuse task255 artifacts.
- Do not export, convert to HF for evaluation, launch an endpoint, promote, push
  main, merge, delete shared files, use 30B, or use 8-GPU.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- If a pass requires export, endpoint, AIME data, additional training, task255,
  30B, or 8-GPU, fail closed and report `BLOCK`.

## Expected Output

- Worker branch and PR if code/docs/status change.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/`.
- Report containing:
  - branch/head/PR or exact blocker;
  - commands/env, local and NemTron paths, source commit, GPU visibility;
  - checkpoint load proof;
  - route change summary or no-change proof;
  - retained canary completion artifacts and checksums, or exact blocker;
  - metrics: prompts requested, completions retained, exact expected-answer
    matches, final-answer marker count, degeneration flags, pass/fail;
  - explicit boundary confirmation.

## Acceptance Criteria

- PASS: task285 iter2 checkpoint loads through an allowed no-export/no-endpoint
  route, all five synthetic non-AIME prompts produce retained completions, and
  canary metrics/artifacts/checksums are complete for review.
- REQUEST-CHANGES: route may work but artifacts, checksums, prompt provenance,
  metrics, or boundary evidence are incomplete.
- BLOCK: route cannot produce retained completions without violating task
  boundaries or hitting a precise unresolved runtime/model issue.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task285, task287, task288, task290
- Related PRs: #350, #352
- Next gate: task291 must pass and be independently reviewed before corrected
  AIME2025/task243 comparison can be released.
