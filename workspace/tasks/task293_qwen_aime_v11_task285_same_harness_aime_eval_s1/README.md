# task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 - corrected AIME2025 FT-vs-base eval

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_3,SESSION=4 -->

## Background

The V11 sequence has reached the corrected AIME2025 comparison gate:

- task276/#344 merged fresh packed Qwen data evidence.
- task283/#349 merged no-training config/import preflight evidence.
- task285/#350 merged bounded Qwen3-4B nonzero-LR SFT smoke evidence.
- task287/#352 recorded the first non-AIME canary route as `BLOCK`.
- task291/#354 merged a repaired no-export/no-endpoint one-GPU synthetic
  non-AIME canary route pass for the task285 iter2 checkpoint.
- task292 approved #354 exact head `2fda1ed46da4c82712a5c22c85bf124c26c6376f`
  as `APPROVE_CANARY_ROUTE_PASS`, with residual risk that one synthetic row used
  `generated_tokens_detokenize_fallback`.

The accepted corrected Qwen3-4B base comparator remains task247:

- base score: `11/30 = 0.36666666666666664`
- base artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`
- base input cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache`
- base score cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`

## Goal

Run or precisely block the corrected AIME2025 same-harness FT-vs-base comparison
for the task285 Qwen3-4B iter2 checkpoint. The comparison can pass only if the
fine-tuned checkpoint scores at least the accepted base `11/30` under the same
corrected evaluator/protocol.

## Inputs

- Current main after #354:
  `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf`
- task291 PR head:
  `2fda1ed46da4c82712a5c22c85bf124c26c6376f`
- task291 evidence source head:
  `dfb6ca64a5479990be9d4f54defb9f294c09866f`
- task291 artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- Candidate checkpoint iteration:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`
- Candidate checkpoint root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`
- Qwen3-4B base model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

## Scope

- Start from current `origin/main`.
- Create worker branch:
  `intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1`.
- Sync code to `/root` before NemTron execution, per project rule.
- Use Qwen3-4B only.
- Use the corrected AIME2025 `30x1` held-out eval/decontam corpus only as eval
  input. Do not use AIME2025 prompts or labels as training data.
- Prefer the merged task291 no-export/no-endpoint local generation route for the
  task285 checkpoint. If the corrected AIME harness cannot be made equivalent
  without export or endpoint, fail closed and report the exact blocker.
- Reuse the accepted task247 base score `11/30` only if prompt source/cache,
  generation settings, parser, denominator, score normalization, and corrected
  protocol are proven compatible with the FT run. If compatibility cannot be
  proven, do not claim FT-vs-base; report `BASE_PROTOCOL_MISMATCH_HOLD` or
  rerun the base only if that can be done within this task's boundaries.

## Boundaries

- Do not train or run optimizer steps.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not reuse task255 artifacts.
- Do not export or convert the task285 checkpoint.
- Do not launch an endpoint.
- Do not promote, claim go/no-go beyond the reported gate result, merge, push
  main, delete shared files, use 30B, or use 8-GPU.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- If a valid comparison requires export, endpoint, task255, AIME2025 train data,
  additional training, 30B, or 8-GPU, stop and report `BLOCK`.

## Expected Output

- Worker branch and PR if code/docs/status/report files change.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/`.
- Official mailbox report with:
  - branch/head/PR or exact blocker;
  - commands/env, local and NemTron paths, source commit, GPU visibility;
  - evaluator/protocol proof versus task247 accepted base;
  - prompt/cache/parser/denominator/normalization evidence;
  - FT summary and raw results artifacts with checksums;
  - prompt count, parsed count, correct count, exact-normalized score, stop/length
    distribution, empty/null/final-marker diagnostics, and any degeneration flags;
  - PASS/FAIL/HOLD against accepted base `11/30`;
  - explicit boundary confirmation.

## Acceptance Criteria

- PASS: task285 FT exact-normalized corrected AIME2025 score is `>= 11/30`
  under the same accepted corrected protocol, with complete artifacts and no
  boundary violations. This pass still does not authorize promotion, export,
  endpoint, 30B, or 8-GPU.
- FAIL: task285 FT exact-normalized corrected AIME2025 score is below `11/30`
  under the same accepted corrected protocol.
- HOLD: protocol equivalence, artifacts, parser/normalization, or base reuse is
  not proven.
- BLOCK: the run cannot proceed within boundaries or requires forbidden export,
  endpoint, training, task255, AIME2025 train data, shared deletion, 30B, or
  8-GPU.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task243, task247, task257, task285, task291, task292
- Gate: this is the first corrected AIME2025 FT-vs-base gate for V11 after
  accepted non-AIME canary route evidence. It does not authorize promotion or
  scale-up.
