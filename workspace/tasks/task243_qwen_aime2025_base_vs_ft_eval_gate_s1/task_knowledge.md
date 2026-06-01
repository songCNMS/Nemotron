# task243_qwen_aime2025_base_vs_ft_eval_gate_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Same-harness base score is mandatory before any FT checkpoint can be judged.
2. Corrected Qwen eval contract uses `/v1/chat/completions`, Qwen checkpoint tokenizer chat template, `enable_thinking=false`, and `truncate_history_thinking=false`.
3. For promotion, FT AIME25 exact-normalized accuracy must be greater than or equal to the matching base score under identical evaluator settings.
4. Session 1 protocol: Qwen3-4B base path is `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`; pilot smoke is corrected AIME2025 original prompts, 30 problems x 1 repeat, `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`, all-request denominator.
5. Session 1 blocker: this worker cannot produce a live base score yet because the configured base model path and corrected AIME score-cache path are missing locally, and `127.0.0.1:13000` / `127.0.0.1:30001` have no endpoint listener.
6. Parsed rate and finish reasons are diagnostics only; FT must pass on exact-normalized accuracy over all request rows, not parser coverage.
