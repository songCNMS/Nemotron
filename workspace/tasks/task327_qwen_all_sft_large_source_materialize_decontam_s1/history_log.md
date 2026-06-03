# task327_qwen_all_sft_large_source_materialize_decontam_s1 - history log

## Session 1 - 2026-06-03 UTC - Assigned by lead

- Created as successor to task322/#388 after lead accepted
  `APPROVE_PARTIAL_EVIDENCE_WITH_EXCLUSIONS / HOLD_FULL_ALL_SFT_PACK_TRAIN`.
- Scope is limited to the 10 task322 `EXCLUDED_SIZE_GT_1GB` sources, with no
  packing, training, eval, export, endpoint, promotion, task255 reuse,
  AIME2025 train data, shared deletion/mutation, main push, merge, or
  self-merge.
- Worker_2 must produce source-by-source materialize/count/checksum/row-manifest
  and decontam evidence, or exact resource/runtime blockers.
