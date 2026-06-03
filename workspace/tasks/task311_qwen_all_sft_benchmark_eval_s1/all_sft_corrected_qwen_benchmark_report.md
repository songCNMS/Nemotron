# task311 corrected Qwen benchmark report

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_3,SESSION=8 -->

## Summary

- Status: `HOLD_NOT_RUN_CANARY_ONLY_RELEASED`
- Blocking precondition: explicit lead release for benchmark evaluation after
  the task311 non-AIME canary report is processed.
- No corrected Qwen benchmark command was launched.
- No base-vs-FT judgment was made.

Lead released only checkpoint-load plus synthetic non-AIME
canary/completion-retention for the task310 salvage checkpoint. That canary was
run under task311 and passed, but benchmark eval remains outside the current
release. This report therefore records no-run benchmark status only.

## Runnable Rows

| Benchmark | Status | Exact blocker |
|---|---|---|
| MMLU-Pro | `HOLD_NOT_RUN` | lead released canary only; benchmark eval awaits explicit post-canary gate |
| AIME2025 | `HOLD_NOT_RUN` | lead released canary only; AIME2025 remains held-out eval/decontam only and awaits explicit post-canary gate |
| HMMT | `HOLD_NOT_RUN` | lead released canary only; benchmark eval awaits explicit post-canary gate |

## Same-Harness Base State

No base-vs-FT comparison was judged. For every benchmark row above, the required
same-harness base artifact selection or rerun remains pending until lead
authorizes the benchmark phase and the exact benchmark runner/protocol is
locked for the task310 checkpoint route.

## Artifacts

No benchmark completions, parser diagnostics, benchmark results, or benchmark
checksum manifests were produced because no benchmark was launched.

Task-owned canary artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`

Canary summary sha256:

`5da06d50f23bd581d2de5988f999cc4a2d7bb162f487afef1033c29810ce93b5`

## Boundary Confirmation

No benchmark eval, AIME/task243 eval, training, AIME2025 train-row creation,
task255 reuse, shared deletion, export, endpoint, promotion, product-code edit,
direct main push, merge, or self-merge occurred.
