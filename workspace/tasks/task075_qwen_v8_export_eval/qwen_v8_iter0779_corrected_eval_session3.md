# Qwen V8 Iter 0779 Corrected Eval - Session 3

## Scope

- Run: `task071_qwen30b_a3b_hard_math_clean_final_v8`
- Source checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`
- HF export: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/hf_export_iter_0000779`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-hard-math-clean-final-v8-iter0000779-hf`
- Remote eval workspace: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval`

## Export Validation

- Export manifest exists: `hf_export_iter_0000779/task071_export_manifest.json`.
- Export contains 16 safetensor shards and `model.safetensors.index.json`.
- Config validation: `model_type=qwen3_moe`, `architectures=["Qwen3MoeForCausalLM"]`, `num_hidden_layers=48`, `num_key_value_heads=4`, `num_experts=128`, `num_experts_per_tok=8`, `max_position_embeddings=262144`.
- Tokenizer validation: tokenizer files exist, chat template present, tokenizer class `Qwen2TokenizerFast`.
- Export manifest records V8 `iter_0000779` as `megatron_checkpoint`. It reused the V7 HF export as the architecture/tokenizer source because the shared `/mnt/3fs` source path returned a remote I/O error during the first export attempt.

## Serving

- Tmux session: `task075_qwen_v8_iter0779_sglang_eval`.
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`, port `30000`.
- `/v1/models` returned `max_model_len=16384`.
- Chat smoke prompt `Reply exactly: ready` returned exact `ready`.
- Endpoint was stopped after full eval completed; GPUs returned to idle.

## Corrected Metrics

| Benchmark | Rows | Accuracy / Score | Parsed Rate | Finish Summary |
|---|---:|---:|---:|---|
| MMLU-Pro corrected chat JSON | 12032 | 0.5606715425531915 | 1.0 | stop 12032 |
| AIME25 corrected original prompt | 300 | 0.19666666666666666 | 0.9533333333333334 | stop 286, length 14 |
| HMMT corrected original prompt | 30 | 13.333333333333334% | 0.6666666666666666 | stop 18, length 12 |

Extra math counters:

- AIME25: `59/300` exact-normalized correct, `73/300` responses contain expected answer, average completion tokens `1874.21`.
- HMMT: `4/30` exact-normalized correct, `8/30` responses contain expected answer, average completion tokens `5595.466666666666`.

## V7 Gate Verdict

| Gate | Threshold | V8 Result | Verdict |
|---|---:|---:|---|
| MMLU-Pro accuracy | >=0.55 | 0.5606715425531915 | pass |
| AIME25 accuracy | >=0.20 | 0.19666666666666666 | fail |
| HMMT exact percent | >=10.0 | 13.333333333333334 | pass |

Overall verdict: V8 does not pass the V7 gate set because AIME25 is short by 1 correct repeat (`59/300`; threshold requires at least `60/300`).

## Artifacts

- SGLang log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/logs/sglang_iter0000779.log`
- MMLU-Pro summary: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/outputs/mmlu_corrected_full/summary.json`
- MMLU-Pro results: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/outputs/mmlu_corrected_full/results.jsonl`
- Math summary: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/outputs/math_corrected_full/summary.json`
- Math results: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/outputs/math_corrected_full/results.jsonl`
