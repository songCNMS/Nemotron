# task257_qwen_aime_v10_task255_same_harness_eval_s1 - History Log

<!-- METADATA:SESSION=2 -->

## Session 0 - Assigned

- Created by `intern_nemotron_lead` for `intern_nemotron_worker_3`.
- Purpose: resume the task243 corrected AIME2025 non-regression gate with the
  task255 Qwen3-4B candidate HF export.
- Accepted base remains Qwen3-4B `11/30 = 0.36666666666666664` from the
  corrected same-harness task247 evidence.
- The candidate FT artifact is
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
- Boundaries: no training, no AIME train data, no promotion, no 30B/8-GPU, and
  no final PASS if task256 blocks or requests changes on artifact integrity.

## Session 1 - 2026-06-01 UTC - Accepted by worker

- Fetched `origin/main` and lead docs branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at `049f380`.
- Created worker branch
  `intern_nemotron_worker_3/task257_qwen_aime_v10_task255_same_harness_eval_s1`
  from current `origin/main`.
- Imported task257 README/history/task_knowledge and updated worker status to
  `Working`.
- Initial focus: verify task256 artifact review status, prove task247 base
  protocol compatibility, then run or hold the task255 same-harness AIME2025
  comparison without FT promotion, training, 30B, or 8-GPU work.

## Session 2 - 2026-06-01 UTC - Same-harness FT eval closeout

- Recorded lead update that task255 PR #329 is OPEN/CLEAN at head
  `d62036e405edc5daa322c09bb89da19b176bb7bf`; the task255 artifact path
  remains
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
- Reused the accepted task247 Qwen3-4B base evidence because the compared
  protocol fields match: AIME2025 30x1, original prompt, 8192 max tokens,
  `/v1/chat/completions`, temperature 0, top_p `1e-5`, same scorer/parser
  shape, same AIME input cache, and all-request denominator.
- Task247 base evidence remained `11/30` exact-normalized accuracy
  `0.36666666666666664`, with 30/30 ok, 23/30 parsed, and cache sha256
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`.
- Launched a task-owned NemTron SGLang endpoint for the task255 HF export on
  `127.0.0.1:13157`, served as
  `task255-qwen3-4b-v10-ft-iter0000001`, with no reasoning parser and
  `/v1/chat/completions` response shape compatible with the task247 base run.
- Ran the corrected AIME2025 same-harness FT eval and copied artifacts to
  `/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/ft_eval/task255_ft_aime2025_30x1_20260601T204900Z/`.
- FT result on the readable exact artifact path: 30/30 ok, finish reasons
  `stop=7,length=23`, parsed `0/30`, correct `0/30`, exact-normalized
  accuracy `0.0`; this is below the accepted base `11/30`.
- Verified the local FT `summary.json` and `endpoint_model_manifest.json` are
  valid JSON; `results.jsonl` has 30 rows.
- Verified NemTron cleanup after the run: no listener on port `13157`, no
  matching `sglang.launch_server` process, and no visible GPU compute process.
- Fetched task256 worker_5 review branch
  `intern_nemotron_worker_5/task256_qwen_aime_v10_task255_artifact_review_s1`
  at `9b77d7ee57293697860095791ad7e6661241abca`; task256 recorded
  REQUEST_CHANGES/HOLD because worker_5 could not directly access the exact
  `/root/task255...` checkpoint/HF export directories for independent hashing.
- Disposition: current exact-path FT run is below base, so the Qwen3-4B
  non-regression result would be FAIL if the task255 artifact is accepted; due
  to task256 REQUEST_CHANGES/HOLD, the overall gate remains HOLD/no promotion.
- Opened PR #330 to `main` for the task257 docs/status closeout.
- No training, AIME train-data use, artifact modification, 30B/8-GPU run,
  promotion claim, main push, or merge was performed.

## Session 2 - 2026-06-01 UTC - Metadata compliance correction

- Corrected worker status metadata after closeout: `status.md` supports only
  `Idle` or `Working`, so the prior `ReadyForPR` value was replaced with
  `Idle` and the current-task field was cleared.
- This is a docs/status compliance update only. PR #330 remains the task257
  closeout PR, and the task257 result/disposition is unchanged: FT `0/30`
  exact-normalized versus accepted base `11/30`, so FAIL versus base, with
  global NO-GO/HOLD because task256 records REQUEST_CHANGES/HOLD.
