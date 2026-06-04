# task333_qwen_all_sft_combined_packed_contract_s1 - task knowledge

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=100 -->

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
7. Task333 combined root `run_20260604T074500Z/packed_qwen_combined_contract`
   exposes 96 packed shards: 84 train, 6 valid, 6 test, using task332 shard
   policy over task299 seed, task329 agentic/structured, and task331 SWE
   no-tools-header shards.
8. Combined metrics are 89,325 packed rows, 342,875,996 input tokens, and
   38,245,535 supervised tokens. Qwen3-30B packed-data validators and
   `sha256sum -c` checks all returned rc 0.
9. Residual decontam nuance: task329/task331 carry prompt-hash,
   normalized-prompt, and n-gram zero-hit fields; task299 seed carries accepted
   task299 prompt-hash and final-answer n-gram evidence but did not emit a
   normalized-prompt hit field.
10. Session 100 corrected the task299 seed row-manifest SHA256s in the
    report/provenance table only: from-m0
    `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599`,
    math-final
    `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653`,
    and hard-verified
    `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f`.
    Metrics, residuals, and `run_20260604T074500Z` artifacts are unchanged.
