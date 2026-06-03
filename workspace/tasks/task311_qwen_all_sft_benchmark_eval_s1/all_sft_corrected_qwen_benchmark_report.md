# task311 corrected Qwen benchmark report

<!-- METADATA:STATUS=Blocker,ASSIGNEE=intern_nemotron_worker_3,SESSION=4 -->

## Summary

- Status: `NOT_STARTED_UPSTREAM_TASK310_HANDOFF_MISSING`
- Blocking precondition: task310 usable checkpoint handoff and non-AIME canary.
- No corrected Qwen benchmark command was launched.
- No base-vs-FT judgment was made.

The corrected Qwen benchmark subset cannot be evaluated yet because task311
must first load the task310 checkpoint and pass a non-AIME canary. The task310
checkpoint path, run root, and artifact handoff are not visible.

## Runnable Rows

| Benchmark | Status | Exact blocker |
|---|---|---|
| MMLU-Pro | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed |
| AIME2025 | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed; AIME2025 remains held-out eval/decontam only |
| HMMT | `BLOCKED_NOT_RUN` | task310 usable checkpoint handoff missing; checkpoint-load/non-AIME canary not passed |

## Same-Harness Base State

No base-vs-FT comparison can be judged without the exact FT checkpoint and route.
For every benchmark row above, the required same-harness base artifact selection
or rerun remains pending until the task310 checkpoint handoff defines the model,
tokenizer, launcher, and protocol.

## Artifacts

No completions, parser diagnostics, benchmark results, or benchmark checksum
manifests were produced because no benchmark was launched.

Task-owned blocker artifact:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T143618Z/manifests/blocker_manifest.json`

Blocker manifest sha256:

`7b90155bc4f31bea4ccb5a67472d0c5d703c5607b0ec0a20d0523bdadc179ed8`

## Boundary Confirmation

No training, AIME2025 train-row creation, task255 reuse, shared deletion, export,
endpoint, promotion, product-code edit, direct main push, or merge occurred.
