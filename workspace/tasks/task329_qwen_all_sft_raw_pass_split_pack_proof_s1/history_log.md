# task329_qwen_all_sft_raw_pass_split_pack_proof_s1 - history log

<!-- METADATA:SESSION=81 -->

## Session 81 - 2026-06-04 UTC - Assigned by lead

- Created as successor to task328/#391 after lead accepted
  `PARTIAL_PASS_WITH_EXACT_BLOCKERS`.
- Scope is restricted to no-training split exposure/parity plus Qwen3-30B
  supervised-token packing proof for the three raw pass sources:
  `instruction-following-structured`, `agentic-interactive`, and `swe`.
- The prior constrained task299 seed remains the only accepted carry-forward
  packed root until this task and a later independent review prove otherwise.
- The nine task327 decontam-hit sources remain excluded fail-closed.
- No training, benchmark eval, export, endpoint, promotion, merge, self-merge,
  or main push is authorized.

## Session 81 - 2026-06-04 UTC - Lead live observation

- Read-only observation found worker_2 local run root
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.
- Initial direct blend attempt failed with `data_prep.rc=1` because the task327
  SWE HF blob path was not readable as parquet.
- Worker_2 materialized task-owned `.jsonl` paths and retried no-training data
  prep. The materialized retry completed with `data_prep_materialized.rc=0`.
- Log-reported data-prep artifact metrics: `num_shards=16`,
  `total_tokens=341849859`, `total_sequences=91315`, `pack_size=4096`; output
  root `packed_qwen_raw_pass_materialized` is about `13G`.
- Worker pane notes a residual: valid/test splits are sparse and shard-based.
  No worker report, PR, mailbox closeout, or lead gate exists yet; this is live
  evidence only and releases no training/eval/export/endpoint/promotion.
