# task309_qwen_all_sft_packed_data_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. The all-SFT packed root must be derived from task308-eligible sources only.
2. Qwen3-30B-A3B packing must use tokenizer-native chat-template behavior; a
   string-level approximation is not enough.
3. AIME2025 rows are allowed only as held-out eval/decontam references, never as
   trainable prompt or label rows.
4. If task308 has no `PASS_AUDIT` inventory/report/output evidence, task309 must
   fail closed instead of treating task299/task276 packed roots as
   all-eligible-SFT authorization.
5. task299 `run_20260602T150941Z` is useful preparatory evidence for Qwen3-30B
   tokenizer/chat-template compatibility and V11 packing/decontam counts, but
   it is not sufficient for all-eligible-SFT task310 release without task308.
