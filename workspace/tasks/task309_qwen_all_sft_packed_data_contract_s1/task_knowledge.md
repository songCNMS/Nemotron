# task309_qwen_all_sft_packed_data_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. The all-SFT packed root must be derived from task308-eligible sources only.
2. Qwen3-30B-A3B packing must use tokenizer-native chat-template behavior; a
   string-level approximation is not enough.
3. AIME2025 rows are allowed only as held-out eval/decontam references, never as
   trainable prompt or label rows.
