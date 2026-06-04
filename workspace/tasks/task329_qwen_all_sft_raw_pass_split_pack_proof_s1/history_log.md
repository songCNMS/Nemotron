# task329_qwen_all_sft_raw_pass_split_pack_proof_s1 - history log

<!-- METADATA:SESSION=3 -->

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

## Session 82 - 2026-06-04 UTC - Worker proof run and closeout

- Created task-owned run root
  `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.
- Initial Qwen30B data-prep attempt failed closed on the SWE HF-cache symlink
  target being read as parquet because the resolved blob lacked a `.jsonl`
  extension.
- Retried with task-owned materialized hardlinks for the three allowed sources:
  task322 `instruction-following-structured`, task322 `agentic-interactive`,
  and task327 `swe`.
- Materialized retry completed with `rc=0`; Qwen packed-data contract validation
  passed for
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Final evidence disposition is `PARTIAL_PASS_WITH_EXACT_BLOCKERS`: SWE packed
  51,029 rows but 0 supervised tokens; structured source had 6
  validation-filtered rows; valid/test split exposure is agentic-only.
- Opened PR https://github.com/songCNMS/Nemotron/pull/392 for task329
  docs/status/helper/report evidence.
- No training, optimizer step, nonzero-LR smoke, eval, export, endpoint,
  promotion, task255 reuse, AIME2025 train rows, shared deletion, main push,
  merge, or self-merge was performed.

## Session 3 - 2026-06-04 UTC - Hook bookkeeping correction

- Fixed worker status metadata to the allowed `Working` status value and set
  task329 bookkeeping to Session 3 for hook compliance.
- Preserved the already-pushed task329/#392 evidence disposition:
  `PARTIAL_PASS_WITH_EXACT_BLOCKERS`.
- No new packing, training, optimizer step, nonzero-LR smoke, eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
  main push, merge, or self-merge was performed.
