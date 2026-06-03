# task311_qwen_all_sft_benchmark_eval_s1 - Qwen all-SFT benchmark evaluation gate

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_3,SESSION=78 -->

## Background

After a new all-SFT checkpoint exists, the coordinator requires non-AIME
canary/checkpoint-load first, then evaluation on available benchmarks. The hard
rule remains: benchmark promotion claims require same-harness base-vs-FT
evidence; this task is eval evidence only, not promotion.

## Goal

Run or prepare corrected same-harness evaluation for all available benchmarks
after task310 checkpoint handoff, and report exact unavailable benchmarks with
reasons.

## Scope

- Use current `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
  after task313/#376 and task310/#373 merged.
- Before any benchmark eval, verify task310 checkpoint-load and run non-AIME
  canary/completion-retention.
- Establish or reuse only valid same-harness base artifacts for the same target
  model/path/protocol before judging FT.
- Evaluate the corrected Qwen subset where runnable:
  - MMLU-Pro;
  - AIME2025;
  - HMMT.
- Evaluate the M1 launcher-available basket where runnable, and record every
  unavailable full-basket row with the exact blocker: missing launcher, missing
  model route, missing dependency, missing data, resource issue, or protocol
  mismatch.
- For each runnable benchmark, produce base and FT metrics, denominator,
  command/env, model/checkpoint paths, prompt/cache proof, completions, parser
  diagnostics, checksum manifests, and residuals.
- AIME2025 is held-out eval/decontam only; never create train rows.

## Boundaries

- No training or optimizer steps.
- No AIME2025 training prompts or labels.
- No task255 reuse.
- No shared deletion under `/mnt/cephfs/data/processing/lei.song`.
- No promotion, production endpoint, direct main push, merge, or product-code
  modification.
- Eval-only export/endpoint is allowed only if required for evaluation and must
  be documented as non-promotion.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1`.
- Reports:
  - `all_sft_non_aime_canary_report.md`;
  - `all_sft_corrected_qwen_benchmark_report.md`;
  - `all_sft_m1_benchmark_availability_report.md`.
- Artifact roots for checkpoint-load/canary and each benchmark, including
  full completions, parser diagnostics, results, summaries, command/env
  manifests, and checksum manifests.
- Mailbox reports at canary and benchmark gates with branch/head/PR or blocker,
  commands/env, artifact paths, metrics, unavailable rows, residuals, and
  pass/fail disposition.

## Acceptance Criteria

- `PASS_EVAL`: checkpoint-load and non-AIME canary pass, runnable benchmarks
  have complete same-harness base-vs-FT artifacts, and unavailable benchmark
  rows are fully explained.
- `REQUEST_CHANGES`: metrics are likely valid but protocol, artifact,
  checksum, unavailable-row, or command/env evidence is incomplete.
- `BLOCK`: checkpoint/canary fails, same-harness base cannot be established, a
  benchmark route is invalid, or boundary violations are observed.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Current main: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Upstream dependency: task310 checkpoint handoff
- Review dependencies: task312, task313
- Gate state: checkpoint-load plus non-AIME canary/completion-retention passed
  at #371 head `2ffbe8c4d9f833980d64d756965e909bf3260f20`. Lead released
  corrected benchmark evaluation for the task310 salvage checkpoint candidate
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`,
  with same-harness base evidence required before judging FT on every benchmark.
  Promotion, training/optimizer steps, task255 reuse, AIME2025 train data,
  shared deletion, self-merge, and main push remain HOLD.
