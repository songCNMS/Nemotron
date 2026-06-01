# task243_qwen_aime2025_base_vs_ft_eval_gate_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. Same-harness base score is mandatory before any FT checkpoint can be judged.
2. Corrected Qwen eval contract uses `/v1/chat/completions`, Qwen checkpoint tokenizer chat template, `enable_thinking=false`, and `truncate_history_thinking=false`.
3. For promotion, FT AIME25 exact-normalized accuracy must be greater than or equal to the matching base score under identical evaluator settings.
