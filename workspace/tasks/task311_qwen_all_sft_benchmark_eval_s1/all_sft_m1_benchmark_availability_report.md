# task311 M1 benchmark availability report

<!-- METADATA:STATUS=Block,ASSIGNEE=intern_nemotron_worker_3,SESSION=12 -->

## Summary

- Status: `BLOCK_LAUNCHER_RUNTIME_MISSING_FOR_REMAINING_M1_ROWS`.
- Corrected Qwen MMLU-Pro/AIME2025/HMMT rows were evaluated through the
  task311 endpoint runner and are reported in
  `all_sft_corrected_qwen_benchmark_report.md`.
- No `nemo-evaluator-launcher` M1 row was executed in Session 12.
- Exact current blocker: neither the local worker environment nor NemTron has
  `nemo-evaluator-launcher`, `nemo-evaluator`, Docker, Slurm, or the required
  benchmark Python modules installed.

This report is fail-closed for M1 launcher rows. The task311 corrected-Qwen
runner supplies same-harness evidence for MMLU-Pro/AIME2025/HMMT, but it is not
the launcher harness for the M1 basket rows.

## Runtime Probe

Local worker probe:

- `which nemo-evaluator-launcher`: not found.
- `which nemo-evaluator`: not found.
- Python modules absent: `nemo_evaluator`, `lm_eval`, `simple_evals`,
  `nemo_skills`, `bfcl_eval`, `tau2_bench`.

NemTron probe:

- `which nemo-evaluator-launcher`: not found.
- `which nemo-evaluator`: not found.
- `which docker`: not found.
- `which sbatch`: not found.
- `which srun`: not found.
- Python modules absent: `nemo_evaluator`, `lm_eval`, `simple_evals`,
  `nemo_skills`, `bfcl_eval`, `tau2_bench`.

The established task071 notes also warn that launcher non-dry execution needs a
launcher/container runtime; current NemTron lacks Docker/Slurm. Session 12
rechecked that this blocker still applies.

## M1 Row Matrix

| Basket row | Launcher mapping | Session 12 status | Exact blocker or evidence |
|---|---|---|---|
| `mmlu_pro` | `lm-evaluation-harness.mmlu_pro` | `CORRECTED_QWEN_RUN_NOT_LAUNCHER_RUN` | Task311 corrected runner produced same-harness base `6758/12032` and FT `6756/12032`, but launcher row not run because launcher runtime is absent |
| `aime25` | `simple_evals.AIME_2025` | `CORRECTED_QWEN_RUN_NOT_LAUNCHER_RUN` | Task311 corrected runner produced FT `16/30` versus accepted task300 base `15/30`, but launcher row not run because launcher runtime is absent |
| `hmmt` | `nemo_skills.ns_hmmt_feb2025` | `CORRECTED_QWEN_RUN_NOT_LAUNCHER_RUN` | Task311 corrected runner produced same-harness base `9/30` and FT `11/30`, but launcher row not run because launcher runtime is absent |
| `gpqa` | `simple_evals.gpqa_diamond` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `hle` | `hle.hle` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `livecodebench` | `livecodebench.codegeneration_release_latest` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `scicode` | `scicode.scicode` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `ifbench` | `ifbench.ifbench` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `ruler_256k` | `ruler.ruler-256k-chat` | `BLOCK_NOT_RUN` | Launcher runtime absent and task311 endpoint context is `16384`, not 256k |
| `aa_lcr` | `AA-LCR.aa_lcr` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `taubench_airline` | `tau2_bench.tau2_bench_airline` | `BLOCK_NOT_RUN` | Launcher runtime absent; module absent; no task311 same-harness base artifact under launcher route |
| `bfcl` | `bfcl.bfclv3` | `BLOCK_NOT_RUN` | Launcher runtime absent; module absent; executable scoring may require external API credentials; no task311 same-harness base artifact under launcher route |
| `mmlu_prox` | `lm-evaluation-harness.mmlu_prox_chat` | `BLOCK_NOT_RUN` | Launcher runtime absent; no task311 same-harness base artifact under launcher route |
| `wmt24pp` | `nemo_skills.ns_wmt24pp` | `BLOCK_NOT_RUN` | Launcher runtime absent; `nemo_skills` absent; no task311 same-harness base artifact under launcher route |
| `multichallenge` | missing | `UNAVAILABLE_EXACT_TASK_MISSING` | No exact launcher task; `mtbench.mtbench-cor1` is not equivalent |
| `terminalbench` | missing | `UNAVAILABLE_EXACT_TASK_MISSING` | Only contamination-detection candidate `codec.terminalbench`; not an equivalent benchmark substitute |
| `mcp_mark` | missing | `UNAVAILABLE_EXACT_TASK_MISSING` | No launcher task found |
| `tool_decathlon` | missing | `UNAVAILABLE_EXACT_TASK_MISSING` | `tooltalk.tooltalk` and `bfcl.bfclv3_ast_prompting` are not equivalent |
| `swe_bench_verified` | missing | `UNAVAILABLE_EXACT_TASK_MISSING` | Only contamination-detection candidate `codec.swebench_test`; not an equivalent benchmark substitute |

## Artifacts

Corrected-Qwen benchmark artifacts:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/`

Consolidated Session 12 artifact summary:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/manifests/session12_benchmark_summary.json`

sha256:

`67998f32982ccf15be7d7eeec55827ec1d5edf658a41ba494d6cb7899e6da828`

## Boundary Confirmation

- No M1 launcher row was run.
- No benchmark substitution was made for missing exact M1 rows.
- No training or optimizer step.
- No AIME2025 train-row creation.
- No task255 reuse.
- No shared deletion.
- Eval-only endpoints were stopped after corrected-Qwen evaluation.
- No promotion, product-code edit, direct main push, merge, or self-merge.
