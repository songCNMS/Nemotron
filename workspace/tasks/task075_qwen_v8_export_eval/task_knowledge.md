# task075_qwen_v8_export_eval - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

- V7 gate protocol: serve Qwen3-30B-A3B HF export with SGLang `tp=4`, `dp=2`, `context_length=16384`, then run corrected full MMLU-Pro, AIME25 `max_tokens=8192`, and HMMT `max_tokens=8192`.
- V7 gate thresholds: MMLU-Pro accuracy `>=0.55`, AIME25 accuracy `>=0.20`, HMMT exact-normalized correct percent `>=10.0`.
- V8 source checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`.
