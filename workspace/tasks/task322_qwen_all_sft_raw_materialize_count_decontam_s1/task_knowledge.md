# task322_qwen_all_sft_raw_materialize_count_decontam_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. Task319 found 12 raw source candidates with repo revisions and HF file
   sha256 coverage, but 0/12 exact local row counts and 0/12
   supervised-token counts.
2. Any source missing local row count, checksum, row manifest, split exposure,
   or decontam proof must be excluded from later packing.
3. AIME2025 prompts/labels remain held-out eval/decontam only.
4. This task does not authorize final packing or training.
5. Task322 resolved all 12 source candidates to exact HF files. The selected
   payload totals `243316402226` bytes.
6. Task322 fully materialized and decontam-checked two bounded sources:
   `instruction-following-structured` with `4969` rows and
   `agentic-interactive` with `19028` rows. Both have 0 parse errors and 0
   task246 heldout prompt-hash/normalized-prompt/13-word-ngram hits.
7. Ten sources remain excluded as `EXCLUDED_SIZE_GT_1GB`; full all-SFT
   materialization needs a separate resource-approved task before any full
   packing contract.
8. Task311 MMLU-Pro input reference is `12032` rows with sha256
   `1c23fc1dae4745edcab672973ef66516cde6ff94f26e59be845a97c072caef36`;
   task314 row-transition reference sha256 is
   `ab338411b96010b3408679f56d42185d69907bfd4a6272c85b8481d3ef077760`.
