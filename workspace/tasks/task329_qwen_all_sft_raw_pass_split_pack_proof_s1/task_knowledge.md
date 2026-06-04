# task329_qwen_all_sft_raw_pass_split_pack_proof_s1 - task knowledge

<!-- METADATA:SESSION=82 -->

1. task328/#391 exact refreshed head
   `7181289cca14af741e7f704b6f34219805822a3e` is approved only as a
   docs/status blocker closeout; it produced no new accepted packed root.
2. The only safe carry-forward packed root before task329 is the constrained
   task299 seed:
   `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
3. The candidate raw pass sources for this task are limited to task322
   `instruction-following-structured`, task322 `agentic-interactive`, and
   task327 `swe`.
4. These sources must not enter training unless source provenance, split
   exposure/parity, heldout/decontam exclusion, Qwen3-30B tokenizer/chat-template
   packing, supervised-token counts, and shard checksums are all proven.
5. All nine task327 `BLOCKED_DECONTAM_HIT` sources remain excluded unless a
   separate later lead-approved false-positive/adjudication task proves safety.
6. A `PASS_RAW_PASS_SPLIT_PACK_PROOF` outcome does not itself release task310;
   it only enables independent packed-contract review.
7. Worker task329 run
   `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`
   produced Qwen3-30B packed artifacts, but the closeout disposition is
   `PARTIAL_PASS_WITH_EXACT_BLOCKERS`.
8. Qwen contract validation passed and intended-vs-exposed shard parity passed,
   but `task327-swe` has `supervised_tokens=0` in packed metrics. This blocks
   treating SWE as a supervised SFT source without later source/config formatter
   remediation.
9. `task322 instruction-following-structured` packed with 6 validation-filtered
   rows; the packed artifact excludes them. Valid/test split exposure is sparse
   and includes only `task322-agentic-interactive`.
10. Task310 should remain unreleased for this raw-pass expansion until lead
    accepts independent review and assigns any needed remediation/combined
    packing follow-up.
