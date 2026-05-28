# task075_qwen_v8_export_eval - Task Knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

- V7 gate protocol: serve Qwen3-30B-A3B HF export with SGLang `tp=4`, `dp=2`, `context_length=16384`, then run corrected full MMLU-Pro, AIME25 `max_tokens=8192`, and HMMT `max_tokens=8192`.
- V7 gate thresholds: MMLU-Pro accuracy `>=0.55`, AIME25 accuracy `>=0.20`, HMMT exact-normalized correct percent `>=10.0`.
- V8 source checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`.
- V8 `iter_0000779` corrected full eval: MMLU-Pro `0.5606715425531915` pass, AIME25 `0.19666666666666666` fail, HMMT exact percent `13.333333333333334` pass; overall V7 gate set fails only on AIME25 by one correct repeat (`59/300`, threshold requires `60/300`).
- V8 HF export artifact path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/hf_export_iter_0000779`; corrected eval artifact root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval`.
