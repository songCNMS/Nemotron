# task327_qwen_all_sft_large_source_materialize_decontam_s1 - history log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-06-03 UTC - Assigned by lead

- Created as successor to task322/#388 after lead accepted
  `APPROVE_PARTIAL_EVIDENCE_WITH_EXCLUSIONS / HOLD_FULL_ALL_SFT_PACK_TRAIN`.
- Scope is limited to the 10 task322 `EXCLUDED_SIZE_GT_1GB` sources, with no
  packing, training, eval, export, endpoint, promotion, task255 reuse,
  AIME2025 train data, shared deletion/mutation, main push, merge, or
  self-merge.
- Worker_2 must produce source-by-source materialize/count/checksum/row-manifest
  and decontam evidence, or exact resource/runtime blockers.

## Session 1 - 2026-06-03 UTC - Acceptance and helper

- Created branch
  `intern_nemotron_worker_2/task327_qwen_all_sft_large_source_materialize_decontam_s1`
  from `origin/main` at `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`.
- Imported task docs from
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `ee4e99a4f009258b4fb56b3d0ca3017e429bf985`.
- Added task-owned helper `materialize_large_sources.py` to stream each large
  selected HF file into a task-owned cache, compute file sha256, count rows,
  write gzipped row manifests, run task246 decontam checks, and emit resource
  evidence. No product code was changed.
