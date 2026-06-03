# task309_qwen_all_sft_packed_data_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

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
6. task308/#374 `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS` makes the
   checksum-backed V11/M1 task299 seed usable as a constrained packed contract,
   while generic `stage1_sft/data_blend_raw` remains excluded until materialized
   row counts, decontam scans, Qwen packing proof, and supervised-token counts
   are available.
7. Task310 should be framed as conditional on the constrained V11/task299 seed;
   it is still no-go for including generic raw SFT registry sources.
8. After the Session 3 constrained-pass refresh, #372 remains hold/no-self-merge
   until lead completes task312 independent review and explicitly releases the
   exact current head.
