# task333_qwen_all_sft_combined_packed_contract_s1 - task knowledge

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_1,SESSION=84 -->

1. #395/task331 merged at `2026-06-04T07:26:34Z` via merge commit
   `ad0c5a7d758d44370695b94c83385591f100c714` from head
   `84c06d4509794ac32257044242b136981d550a7c`; accepted evidence is
   `PASS_SWE_SUPERVISED_UNBLOCK / HOLD_TRAINING`.
2. task331 SWE root:
   `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z`.
   Metrics: 51,029 rows, 16 shards, 209,014,784 input tokens, 28,524,315
   supervised tokens, Qwen3-30B contract pass. Residuals: SWE-only proof, raw
   source has no upstream split metadata, and all rows still truncate to 4096.
3. #394/task332 merged at `2026-06-04T07:03:52Z` via merge commit
   `86eea012e7dd9d382a02f786826fa71dcc4521e5`; accepted evidence is
   `PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING / HOLD_TRAINING`.
4. task332 split policy is `task332_per_source_shard_holdout_v1`:
   per-source `row_index % 16`, remainder 14 valid, remainder 15 test, all
   other rows train. Six structured rows are fail-closed excluded by exact
   row index/hash unless a later task repairs tool context and reruns validator.
5. #392/task329 is partial evidence only. Its raw-pass packed root is not an
   accepted training contract because SWE was zero supervised tokens, structured
   had six validation-filtered rows, valid/test exposure was sparse, and task299
   combination was deferred.
6. The task333 product is still no-training evidence. Even a PASS disposition
   only enables a later independent review task; task310 remains HOLD until that
   review and lead gate accept the combined contract.
