# task247_qwen_aime2025_qwen4b_base_smoke_s1 - History Log

<!-- METADATA:SESSION=2 -->

## Session 0 - Assigned

- Created by `intern_nemotron_lead` for `intern_nemotron_worker_3`.
- Purpose: turn the merged task243 same-harness protocol into the first real
  Qwen3-4B base AIME2025 pilot artifact or a precise blocker.
- Initial disposition: Assigned; no FT judgment or training in this task.

## Session 1 - 2026-06-01 UTC - Base smoke artifact produced

- Accepted task on branch
  `intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1` from
  `origin/main` after PR #321 merge commit
  `20973e78f196d7e5d71993f60dc74a3500223f5f`.
- Confirmed approved Qwen3-4B base checkpoint path exists:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Confirmed local/common endpoints `127.0.0.1:13000` and `127.0.0.1:30001`
  were unavailable.
- Created a task-owned AIME2025 evaluator cache from pinned
  `opencompass/AIME2025` revision `a6ad95f611d72cf628a80b58bd0432ef6638f958`
  with `30` rows, `30` unique problems, and `1` request per problem.
- Launched a task-owned single-GPU Qwen3-4B base SGLang endpoint on `NemTron`
  port `13147`; no FT, training, 30B, or 8-GPU launch was performed.
- First endpoint attempt with `--reasoning-parser qwen3` produced
  `message.content=null` and was retained only as a failed diagnostic.
- Reran the same task243 runner against the endpoint without reasoning parser.
  Valid base AIME2025 pilot result: `11/30` exact-normalized correct,
  accuracy `0.36666666666666664`, `30/30` requests ok, parsed `23/30`,
  finish reasons `stop=21,length=9`.
- Copied required artifacts locally under
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`.
- Stopped the task-owned Qwen3-4B endpoint after artifact collection and
  verified no listener remained on port `13147`.
- Added `qwen4b_base_smoke_report.md` and marked task docs `ReadyForPR`.
- Opened PR #326 for the task247 report branch.

## Session 2 - 2026-06-01 UTC - PR merged and task closed

- Received lead approval to self-merge PR #326 if it remained `CLEAN`.
- Verified PR #326 immediately before merge: state `OPEN`, base `main`,
  head `8fb34bd9116e32aa8d191750f2510d2a843e0da5`,
  `mergeStateStatus=CLEAN`.
- Merged PR #326 with merge commit
  `85f2bf5c11062741388ca114a84a2c26535b7df9` at
  `2026-06-01T17:21:29Z`.
- Post-merge state: PR #326 is `MERGED`; no post-merge issue observed.
- Final disposition remains Qwen3-4B base pilot only: `11/30`
  exact-normalized accuracy `0.36666666666666664`, same-harness FT comparison
  must use the same cache, runner, prompt, sampling, and all-request
  denominator.
- Marked task metadata `Completed` and worker status `Idle`.
