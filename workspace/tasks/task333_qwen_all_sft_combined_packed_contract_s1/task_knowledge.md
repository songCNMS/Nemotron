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
7. Session 86 request-changes blocker for #396 head
   `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`: report table values
   `5894818a7fcfea644e202da10f551f3de844b8369432221c376e5121ef80cd15`,
   `ca07a194e74131b726252bd2589a83c0572ef9bb04c426b710032fcbdc1bb521`, and
   `f1373026c688817a7e47f6060878f975e9bf125e959aee6375bcf49149cf4820` must be
   reconciled against actual task333 artifact/source_provenance values
   `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599`,
   `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653`, and
   `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f` before
   #396 can be approved.
8. Worker_1 submitted #396 fix head
   `9a9471e35e3d80f6bf2995478ddf4bd1ef785a66`; lead verified the stale hashes
   are absent and the three `run_20260604T074500Z` values are present. Approval
   still requires refreshed independent review because #396 head changed after
   task334's original `REQUEST_CHANGES_REPORT_ARTIFACT_MISMATCH` report.
9. Worker_1 later pushed metadata-only head
   `6261daaa37172caa11929b0b88f685b63f987221`; the task333 report is unchanged
   from head `9a9471e3`. Current exact-head review target is `6261daaa`.
10. After #397/task334 merged at `35b6d649cf15eddf09978628f60522b9416607af`,
    #396 exact head `6261daaa37172caa11929b0b88f685b63f987221` was approved by
    lead comment `issuecomment-4620438023` for worker_1 self-merge only if
    exact/CLEAN. No task310/training/eval/export/endpoint/promotion/30B release.
