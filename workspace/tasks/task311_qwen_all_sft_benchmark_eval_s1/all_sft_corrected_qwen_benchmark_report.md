# task311 corrected Qwen benchmark report

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_3,SESSION=10 -->

## Summary

- Status: `HOLD_EVAL_ONLY_EXPORT_ENDPOINT_ROUTE_REPORT_BEFORE_RUN`
- Blocking precondition: lead processing of the Session 9 route report before
  any benchmark row that needs eval-only export or endpoint is launched.
- No corrected Qwen benchmark command was launched.
- No base-vs-FT judgment was made.

Lead accepted the task311 non-AIME canary and released benchmark-eval phase
work, then clarified that any row requiring export or endpoint must first be
reported as an eval-only route/blocker. The established corrected Qwen
MMLU-Pro/AIME2025/HMMT route is endpoint-based for task071/task300 artifacts,
while task310 is a Megatron checkpoint. This report therefore records the
required route gate and no-run benchmark status.

## Runnable Rows

| Benchmark | Status | Exact blocker |
|---|---|---|
| MMLU-Pro | `HOLD_NOT_RUN` | task310 is Megatron checkpoint; established corrected runner is endpoint-based; report eval-only export/endpoint route before running or implement no-export base+FT rerun |
| AIME2025 | `HOLD_NOT_RUN` | accepted task300 base is endpoint/SGLang; direct task306 route has sampling/backend residual, so exact same-harness judgment needs either eval-only export/endpoint FT under task300 protocol or same-route no-export base rerun first |
| HMMT | `HOLD_NOT_RUN` | established corrected runner is endpoint-based; HMMT input exists locally but not yet materialized on NemTron task311 root; report eval-only export/endpoint route before running or implement no-export base+FT rerun |

## Same-Harness Base State

No base-vs-FT comparison was judged. For every benchmark row above, the required
same-harness base artifact selection or rerun remains open:

- Endpoint route: reuse prior base only when model path, evaluator, prompt
  protocol, sampling, parser, route, and denominator match exactly; otherwise
  rerun base under the same endpoint route.
- Direct no-export route: rerun base from task298 imported Megatron checkpoint
  and run FT from task310 `iter_0000035` through the same task-owned direct
  evaluator before judging FT.

## Artifacts

No benchmark completions, parser diagnostics, benchmark results, or benchmark
checksum manifests were produced because no benchmark was launched.

Task-owned canary artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`

Canary summary sha256:

`5da06d50f23bd581d2de5988f999cc4a2d7bb162f487afef1033c29810ce93b5`

Session 9 route report:

`workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/all_sft_benchmark_route_gate_report.md`

## Boundary Confirmation

No benchmark eval, AIME/task243 eval, training, AIME2025 train-row creation,
task255 reuse, shared deletion, export, endpoint, promotion, product-code edit,
direct main push, merge, or self-merge occurred.
