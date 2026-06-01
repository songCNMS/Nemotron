# task241_qwen_aime_v10_sidecar_data_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. V10 sidecar work must not train on AIME 2025 prompts or labels; AIME25 is held-out eval/decontam material only.
2. Existing V9 recurrence sidecar coverage was too sparse for `aime_06`: task076 found only one `chairs`, one `binary string`, four explicit DP/dynamic-programming rows, and no combined no-111-like DP rows.
3. Qwen SFT packing must preserve tokenizer-native chat-template rendering with `enable_thinking=false` and `truncate_history_thinking=false`.
