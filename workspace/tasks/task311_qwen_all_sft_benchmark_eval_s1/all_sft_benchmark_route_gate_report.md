# task311 benchmark route gate report

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_3,SESSION=10 -->

## Summary

- Task: `task311_qwen_all_sft_benchmark_eval_s1`
- PR: `#371`
- Branch:
  `intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1`
- Current branch head before this report:
  `2ffbe8c4d9f833980d64d756965e909bf3260f20`
- Base main:
  `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Task310 FT checkpoint:
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`
- Base model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Task298 imported base Megatron checkpoint:
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`
- Accepted canary:
  `PASS_NON_AIME_CANARY_ONLY` at
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`
- Current disposition:
  `HOLD_EVAL_ONLY_EXPORT_ENDPOINT_ROUTE_REPORT_BEFORE_RUN`

Lead accepted the task311 non-AIME canary and released the benchmark-eval phase,
then clarified that any row requiring export or endpoint must first be reported
as an eval-only route/blocker before running it. This report records that route
analysis. No benchmark command, export, endpoint, training, optimizer step,
promotion, direct main push, merge, self-merge, task255 reuse, shared deletion,
or AIME2025 train-row use was performed in Session 9.

## Corrected Qwen Routes

| Benchmark | Current input/evaluator evidence | Same-harness base status | Route disposition |
|---|---|---|---|
| AIME2025 | Accepted task300 base artifacts exist for endpoint route; task306 no-export evaluator exists for Megatron checkpoints | Accepted task300 base `15/30` is endpoint/SGLang `/v1/chat/completions`, `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`, original prompt, corrected parser/normalizer, all-request denominator | Endpoint route can reuse task300 base only if task310 FT is eval-only exported and served under the same protocol. Direct no-export route would require rerunning base from task298 imported Megatron checkpoint before judging FT |
| HMMT | Corrected task071 math endpoint evaluator exists; HMMT February 2025 input is available locally under HF cache, but not yet materialized on NemTron task311 root | No task311 same-harness base artifact exists for task310 route | Endpoint route requires eval-only export/endpoint and base-vs-FT run. Direct no-export route would require a task-owned runner and base rerun from task298 imported Megatron checkpoint |
| MMLU-Pro | Corrected task071 MMLU-Pro endpoint evaluator exists; `TIGER-Lab/MMLU-Pro` test split can be materialized locally | No task311 same-harness base artifact exists for task310 route | Endpoint route requires eval-only export/endpoint and base-vs-FT run. Direct no-export route would require a task-owned runner and base rerun from task298 imported Megatron checkpoint |

## Endpoint / Export Requirement

The repo's established corrected Qwen full-benchmark route for MMLU-Pro,
AIME2025, and HMMT is endpoint-based:

- MMLU-Pro runner:
  `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_mmlu_pro_eval.py`
- AIME2025/HMMT runner:
  `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py`
- Task300 accepted base AIME route:
  eval-only SGLang endpoint direct from the base HF path, `/v1/chat/completions`,
  `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`, corrected parser and
  all-request denominator.

Task310 is a Megatron checkpoint, not an HF directory. To run the established
endpoint route against task310, the required route is:

1. Eval-only HF export of
   `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`
   using source metadata/tokenizer
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
2. Eval-only SGLang endpoint serving the exported task310 checkpoint on a
   task-owned port with `tp=4`, `dp=2`, 16k context, and no production endpoint
   claim.
3. FT benchmark runs through the same endpoint payload semantics as the
   accepted base route, retaining full completions, parser diagnostics,
   command/env manifests, endpoint manifests, and checksum manifests.
4. Base evidence for each benchmark must either be reused only when model path,
   route, evaluator, prompt protocol, sampling, parser, and denominator match
   exactly, or rerun under the identical task311 endpoint route before FT is
   judged.

No eval-only export or endpoint was launched because lead requested this
route/blocker report first.

## Direct No-Export Alternative

The canary and task306 AIME run prove that a direct Megatron/MCore route can
load 30B Megatron checkpoints without export or endpoint. A fully same-harness
direct route would need:

- task298 imported base Megatron checkpoint as base input;
- task310 `iter_0000035` as FT input;
- one task-owned evaluator implementation per benchmark prompt/parser contract;
- identical base and FT route, prompt protocol, sampling, parser, normalizer,
  selected-rank policy, and denominator.

This route avoids endpoint/export but cannot reuse the accepted task300 endpoint
base as exact same-harness evidence. It requires new base runs before any FT
judgment. It is also not equivalent to nemo-evaluator-launcher basket rows
unless each row's prompt, scoring, and data contract are implemented and
documented in the task-owned direct runner.

## M1 Basket Availability

Exact launcher mapping from
`src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml`
contains these rows:

| Basket row | Launcher status | Session 9 task311 disposition |
|---|---|---|
| `mmlu_pro` | `available`: `lm-evaluation-harness.mmlu_pro` | Route report only; requires same-harness base plus FT route |
| `aime25` | `available`: `simple_evals.AIME_2025` | Route report only; AIME2025 eval/decontam only |
| `hmmt` | `available`: `nemo_skills.ns_hmmt_feb2025` | Route report only; requires same-harness base plus FT route |
| `gpqa` | `available`: `simple_evals.gpqa_diamond` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `hle` | `available`: `hle.hle` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `livecodebench` | `available`: `livecodebench.codegeneration_release_latest` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `scicode` | `available`: `scicode.scicode` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `ifbench` | `available`: `ifbench.ifbench` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `ruler_256k` | `available`: `ruler.ruler-256k-chat` | Unrun; blocked for 30B 16k endpoint route because row name requires 256k context |
| `aa_lcr` | `available`: `AA-LCR.aa_lcr` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `taubench_airline` | `available`: `tau2_bench.tau2_bench_airline` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `bfcl` | `available`: `bfcl.bfclv3` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `mmlu_prox` | `available`: `lm-evaluation-harness.mmlu_prox_chat` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `wmt24pp` | `available`: `nemo_skills.ns_wmt24pp` | Unrun; requires eval-only endpoint/launcher route plus same-harness base |
| `multichallenge` | `missing` | Unavailable: no exact launcher task; `mtbench.mtbench-cor1` is not equivalent |
| `terminalbench` | `missing` | Unavailable: only contamination-detection candidate `codec.terminalbench`; not equivalent |
| `mcp_mark` | `missing` | Unavailable: no launcher task found |
| `tool_decathlon` | `missing` | Unavailable: `tooltalk.tooltalk` and `bfcl.bfclv3_ast_prompting` are not equivalent |
| `swe_bench_verified` | `missing` | Unavailable: only contamination-detection candidate `codec.swebench_test`; not equivalent |

## Probes Performed

- Verified local branch is based on `origin/main`
  `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`.
- Verified NemTron host `lg-cmc-b7r201-f08u26-h200-000126` had eight idle
  H200s at probe time.
- Verified task300/task306 AIME input cache paths exist locally.
- Verified task300 AIME input cache exists on NemTron.
- Verified HMMT February 2025 JSONL exists locally in HF cache; the same exact
  local path was not present on NemTron at probe time.
- Verified `TIGER-Lab/MMLU-Pro` test split can be materialized locally with
  `12032` rows.
- Verified ports `13231`-`13234` were free on NemTron at probe time.

## Boundary Confirmation

- No benchmark command was launched.
- No eval-only export was launched.
- No endpoint was launched.
- No training or optimizer step.
- No AIME2025 prompts or labels used as trainable data.
- No task255 reuse.
- No shared deletion under `/mnt/cephfs/data/processing/lei.song`.
- No promotion or go/no-go claim.
- No product-code edit.
- No direct main push, merge, or self-merge.
