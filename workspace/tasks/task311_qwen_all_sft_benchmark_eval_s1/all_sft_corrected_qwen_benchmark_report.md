# task311 corrected Qwen benchmark report

<!-- METADATA:STATUS=FailMixed,ASSIGNEE=intern_nemotron_worker_3,SESSION=12 -->

## Summary

- Status: `FAIL_MMLU_PRO_BELOW_BASE_WITH_AIME_HMMT_PASS`.
- Task: `task311_qwen_all_sft_benchmark_eval_s1`.
- PR: `#371`.
- Branch head before Session 12 commit:
  `1ce85c6382d0587a35ab02830c0d08b7c874c5b3`.
- Local artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z`.
- NemTron artifact root:
  `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z`.
- Task310 FT checkpoint:
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`.
- Eval-only HF export:
  `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/hf_export/task310_iter_0000035_hf`.
- Base model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

Lead accepted the Session 10 route-gate report and released eval-only
export/endpoint plus same-harness benchmark execution. Session 12 completed
eval-only HF export, endpoint preflight, corrected AIME25 FT, same-route HMMT
base plus FT, and same-route MMLU-Pro base plus FT. No promotion claim is made:
MMLU-Pro FT is below same-route base by 2 rows.

## Disposition

| Benchmark | Base | FT | Delta | Disposition |
|---|---:|---:|---:|---|
| AIME2025 | accepted task300 `15/30 = 0.5` | `16/30 = 0.5333333333333333` | `+1` | `PASS_VS_BASE` |
| HMMT Feb 2025 | `9/30 = 0.3` | `11/30 = 0.36666666666666664` | `+2` | `PASS_VS_BASE` |
| MMLU-Pro test | `6758/12032 = 0.5616688829787234` | `6756/12032 = 0.5615026595744681` | `-2` | `FAIL_VS_BASE` |

Overall corrected-Qwen disposition is `FAIL_MMLU_PRO_BELOW_BASE`. AIME2025 and
HMMT improved under the corrected endpoint route, but MMLU-Pro regressed
slightly under the same input, prompt, parser, sampling, and all-request
denominator.

## Protocol

- Endpoint route: eval-only SGLang OpenAI-compatible
  `/v1/chat/completions`.
- Endpoint host: NemTron `lg-cmc-b7r201-f08u26-h200-000126`.
- Endpoint port: task-owned `13231`, used sequentially for FT and base.
- GPU shape: `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`, SGLang
  `tensor-parallel-size=4`, `data-parallel-size=2`, context length `16384`.
- Sampling: `temperature=0.0`, `top_p=1e-5`.
- AIME/HMMT max tokens: `8192`; parser is last boxed value with normalized
  exact match; denominator is all requested rows.
- MMLU-Pro max tokens: `64`; prompt is chat JSON answer-only; parser reads
  JSON answer field A-J with answer-colon and letter fallback; denominator is
  all requested rows.
- AIME base reuse: accepted task300 base was reused because the FT run matched
  the Qwen3-30B model family, endpoint route, `/v1/chat/completions` payload
  semantics, original prompt, sampling, parser, normalizer, and denominator.
- HMMT/MMLU-Pro base: no accepted base artifact existed, so task311 reran base
  through the same endpoint route before judging FT.

## Export Evidence

Eval-only export command is retained at:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/logs/export_command.txt`

Export manifest:

- Local:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/manifests/eval_only_hf_export_manifest.json`
- Remote:
  `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/manifests/eval_only_hf_export_manifest.json`
- Disposition: `EXPORT_PASS`.
- Export elapsed: `183.892` seconds.
- HF export files: `26`; safetensor shards: `16`; total bytes:
  `61084232276`.
- Manifest sha256:
  `74524dcf284beb655b154e4d043a8742248353ef85cb040f7de1e6ca6660fc42`.
- HF export checksum manifest sha256:
  `45db4797ed0a2c833fc8a2278210431d56a4e332017ada9cbff0ca3cbff798b5`.

HF metadata preflight passed: `AutoConfig` loaded `qwen3_moe`,
architecture `Qwen3MoeForCausalLM`, and `AutoTokenizer` loaded
`Qwen2TokenizerFast` with chat template.

## Input Evidence

Input manifest:

- Local:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/input/input_manifest.json`
- Remote:
  `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/input/input_manifest.json`
- sha256:
  `c645afcdbd88a43b447b6e3d1585df77d1c19b442a6256b1c0a2630a2f9cb053`.

Inputs:

- AIME2025 cache copied from accepted task300 input bundle:
  `aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`.
- HMMT source:
  `/root/.cache/huggingface/hub/datasets--PraMamba--HMMT-202502/snapshots/9de5288c84abeb090b162f75e43a96ad971c7b26/hmmt_feb_2025.jsonl`.
- MMLU-Pro source: `TIGER-Lab/MMLU-Pro` test split from local HF cache,
  materialized to `mmlu_pro/mmlu_pro_test.jsonl` with `12032` rows.

## Artifact Matrix

| Run | Local summary | Summary sha256 | Key metrics |
|---|---|---|---|
| AIME25 FT | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/ft_aime25_task310_20260603T181900Z/summary.json` | `d19713736d34a102ceb8af5aa35d3c05e822d469810f7f63743295ddae21ae47` | `16/30`, parsed `19/30`, finish `stop=18,length=12` |
| HMMT base | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/base_hmmt_task311_20260603T183100Z/summary.json` | `1466e9d29528bb6fbbc4c8b781e9043d1a0239d458e34059fb24fa9616f68843` | `9/30`, parsed `18/30`, finish `stop=16,length=14` |
| HMMT FT | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/ft_hmmt_task310_20260603T183800Z/summary.json` | `a4ec85ca9582fc84d135aae4c6db9a3aae40741112be385537bd9cc612c1e94c` | `11/30`, parsed `19/30`, finish `stop=18,length=12` |
| MMLU-Pro base | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/base_mmlu_pro_task311_20260603T183600Z/summary.json` | `fe2247bd2a861f8c327f652211b8d7b52b4ec8a4f4115242cbb839e72975a917` | `6758/12032`, parsed `12032/12032`, finish `stop=12032` |
| MMLU-Pro FT | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/ft_mmlu_pro_task310_20260603T184300Z/summary.json` | `0d6b12f55e350584fa9f198273173292060bdcef1da3998618eaca354f8d0108` | `6756/12032`, parsed `12032/12032`, finish `stop=12032` |

Each run directory also contains `results.jsonl`, `full_completions.jsonl`,
`parser_diagnostics.jsonl`, `manifests/*_row_manifest.jsonl`,
`manifests/command_env_manifest.json`, `manifests/endpoint_manifest.json`,
`logs/run.log`, and `checksum_manifest.json`.

Consolidated Session 12 artifact summary:

- Path:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/manifests/session12_benchmark_summary.json`
- sha256:
  `67998f32982ccf15be7d7eeec55827ec1d5edf658a41ba494d6cb7899e6da828`.

## Endpoint Cleanup

- FT endpoint initial start evidence:
  `endpoint/task310_ft_13231/`.
- Base endpoint evidence:
  `endpoint/base_13231/`.
- FT restart evidence:
  `endpoint/task310_ft_13231_restart/`.
- Each endpoint directory includes `server_command.txt`, start manifest,
  SGLang log, PID file, models probe, and post-stop check.
- Final post-stop probe: port `13231` free, no `sglang.launch_server` process,
  and GPUs idle (`1 MiB` each in the final compute-process check).

## Residuals

- AIME/HMMT have substantial length-finish residuals at 8192 max tokens.
- MMLU-Pro is highly deterministic under this prompt shape but FT is below
  base by 2 rows; treat as a corrected-Qwen failure for that row.
- This is eval evidence only. It is not promotion, not product endpoint
  approval, and not a training decision.

## Boundary Confirmation

- No training or optimizer step.
- No AIME2025 prompts or labels used as trainable data.
- AIME2025 was used only as held-out eval input.
- No task255 reuse.
- No shared deletion under `/mnt/cephfs/data/processing/lei.song`.
- Eval-only export and endpoints were used only for this task-owned benchmark
  evidence and were stopped afterward.
- No promotion, product-code edit, direct main push, merge, or self-merge.
