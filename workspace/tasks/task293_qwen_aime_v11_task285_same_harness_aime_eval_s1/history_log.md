# task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 - history log

<!-- METADATA:SESSION=1 -->

## Session 76 - 2026-06-02 UTC - assignment

- Created after #354/task291 merged no-export/no-endpoint synthetic non-AIME
  canary route pass evidence and task292 approved the exact #354 head as
  `APPROVE_CANARY_ROUTE_PASS`.
- Assigned to worker_3 for corrected AIME2025 same-harness FT-vs-base eval or
  precise fail-closed blocker.
- Accepted base comparator remains Qwen3-4B task247 `11/30 =
  0.36666666666666664`; worker_3 must prove protocol equivalence before using
  it.
- Boundaries: no training, AIME2025 train data, task255 reuse, export, endpoint,
  promotion, shared deletion, main push, merge, 30B, or 8-GPU.
- Delivered assignment to worker_3 after processing task292 #355 follow-up
  mailbox. Required output is branch/head/PR or exact blocker, commands/env,
  artifact roots, same-harness protocol proof, FT metrics, checksums, and
  PASS/FAIL/HOLD/BLOCK against the accepted base `11/30`.
- Observed worker_3 acceptance branch at
  `6fbaf68ac84e94e8bccfe74145db8aa21bb8be75`; it is docs/status only and
  diff-check clean, but based on `34de04ff...` before #355 merged. Sent
  delivered follow-up requiring refresh/rebase to current main `228ffd74...`
  before any PR or final evidence.
- Processed worker_3 refresh mailbox: branch is now
  `b120dc9ea747a8bb5052be707a256ddc1694e8f2` on current main
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a`. Lead recheck confirms the branch
  is still docs/status only and diff-check clean. Awaiting official AIME eval
  result, PR, or precise fail-closed blocker.
- Observed branch head `87de0a97e6c0406a4b67520faab6b11d91d9131e` adding a
  no-export AIME eval runner. Read-only live run `run_20260602T085237Z` is
  active on NemTron PID `433268`; partial progress is `2/30` with one correct
  and one incorrect. Only manifests are present so far; no final summary,
  results, checksums, official worker report, or PR exists yet.
- Follow-up read-only observation reached `6/30`, parsed `6/6`, correct `5/6`;
  PID `433268` remains active and no final artifacts or official report exist.
  This remains non-gating partial evidence.
- Follow-up read-only observation reached `8/30`, parsed `8/8`, correct `5/8`;
  PID `433268` remains active and only manifests exist remotely. No final
  summary/results/checksums, official worker report, or PR exists yet.
- Follow-up read-only poll after additional wait: PID `433268` still active at
  about 25 minutes elapsed, last logged progress still `8/30`, and mailbox/
  final artifacts remain absent. Continue waiting for worker-owned completion or
  blocker report.
- Follow-up read-only poll: PID `433268` still active at about 29 minutes
  elapsed; progress reached `9/30`, correct `5/9`, with `aime_09_r01` stopped
  on length and unparsed. No final artifacts, official report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 33 minutes
  elapsed; progress reached `10/30`, correct `5/10`, with `aime_09_r01` and
  `aime_10_r01` stopped on length and unparsed. No final artifacts, official
  report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 39 minutes
  elapsed; progress reached `11/30`, correct `5/11`, with `aime_09_r01`,
  `aime_10_r01`, and `aime_11_r01` stopped on length and unparsed. No final
  artifacts, official report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 45 minutes
  elapsed; progress reached `12/30`, correct `5/12`, with `aime_09_r01`
  through `aime_12_r01` stopped on length and unparsed. No final artifacts,
  official report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 50 minutes
  elapsed; progress reached `13/30`, correct `5/13`, with `aime_13_r01`
  stopped, parsed, and incorrect. No final artifacts, official report, or PR
  exists yet.
- Follow-up read-only poll: PID `433268` still active at about 54 minutes
  elapsed; progress reached `14/30`, correct `5/14`, with `aime_14_r01`
  stopped, parsed, and incorrect. No final artifacts, official report, or PR
  exists yet.
- Follow-up read-only poll: PID `433268` still active at about 61 minutes
  elapsed; progress reached `16/30`, correct `6/16`, with `aime_15_r01`
  stopped, parsed, and incorrect and `aime_16_r01` stopped, parsed, and
  correct. No final artifacts, official report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 62 minutes
  elapsed; progress reached `17/30`, correct `7/17`, with `aime_17_r01`
  stopped, parsed, and correct. No official report or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 69 minutes
  elapsed; progress reached `19/30`, correct `8/19`, with `aime_18_r01`
  length-stopped and unparsed and `aime_19_r01` stopped, parsed, and correct.
  No final artifacts, official report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 78 minutes
  elapsed; progress reached `20/30`, correct `8/20`, with `aime_20_r01`
  stopped, parsed, and incorrect. No final artifacts, official report, or PR
  exists yet.
- Follow-up read-only poll: PID `433268` still active at about 80 minutes
  elapsed; progress reached `21/30`, correct `9/21`, with `aime_21_r01`
  stopped, parsed, and correct. No official report or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 82 minutes
  elapsed; progress reached `22/30`, correct `10/22`, with `aime_22_r01`
  stopped, parsed, and correct. No final artifacts, official report, or PR
  exists yet.
- Follow-up read-only poll: PID `433268` still active at about 88 minutes
  elapsed; progress reached `23/30`, correct `10/23`, with `aime_23_r01`
  length-stopped and unparsed. No final artifacts, official report, or PR
  exists yet.
- Follow-up read-only poll: PID `433268` still active at about 93 minutes
  elapsed; progress reached `24/30`, correct `11/24`, with `aime_24_r01`
  stopped, parsed, and correct. This matches the accepted base numerator but is
  still non-gating pending all 30 rows plus final artifacts and official
  worker report. No final artifacts, official report, or PR exists yet.
- Follow-up read-only poll: PID `433268` still active at about 101 minutes
  elapsed; progress reached `26/30`, correct `11/26`, with `aime_25_r01` and
  `aime_26_r01` stopped, parsed, and incorrect. No final artifacts, official
  report, or PR exists yet.
- Follow-up read-only poll at `2026-06-02T10:40:55Z`: PID `433268` still
  active at about 106 minutes elapsed; progress reached `27/30`, correct
  `12/27`, with `aime_27_r01` stopped, parsed, and correct. Remote artifacts
  still only contain prompt/checkpoint-load/command-env manifests. No final
  summary/results/checksums, official worker report, or PR exists yet.
- Follow-up read-only poll at `2026-06-02T10:46:45Z`: PID `433268` still
  active at about 113 minutes elapsed; progress reached `28/30`, correct
  `12/28`, with `aime_28_r01` length-stopped, unparsed, and incorrect. Remote
  artifacts still only contain prompt/checkpoint-load/command-env manifests. No
  final summary/results/checksums, official worker report, or PR exists yet.
- Follow-up read-only poll at `2026-06-02T10:52:27Z`: PID `433268` still
  active at about 119 minutes elapsed; progress reached `29/30`, correct
  `12/29`, with `aime_29_r01` length-stopped, unparsed, and incorrect. Remote
  artifacts still only contain prompt/checkpoint-load/command-env manifests. No
  final summary/results/checksums, official worker report, or PR exists yet.
- Final read-only artifact observation at `2026-06-02T10:57:43Z`: the NemTron
  process exited, log reached `30/30`, and the runner printed
  `TASK293_DISPOSITION=PASS`.
- Artifact roots:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`
  and
  `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/artifacts`.
- Summary metrics: FT `12/30 = 0.4`; accepted base `11/30 =
  0.36666666666666664`; delta `+1/30`; parsed `21/30`; finish reasons length
  `9`, stop `21`; total requests `30`; disposition reason says FT
  exact-normalized score is greater than or equal to accepted base.
- Artifacts: `aime_eval/results.jsonl` 30 rows, `aime_eval/full_completions.jsonl`
  30 rows, `aime_eval/summary.json`, prompt/checkpoint-load/command-env
  manifests, and checksum manifest. Local synced artifacts pass checksum
  validation via manifest relative paths; explicit NemTron `sha256sum` values
  match the manifest.
- Same-harness proof claims prompt-token match with task247 base, same AIME score
  cache, same 30-row denominator, same max tokens, same prompt variant, and same
  corrected parser/normalizer. Residual: `sampling_exact_parameter_match=false`;
  task293 claims deterministic greedy semantic match between task247 endpoint
  temperature-zero decode and local MCore top-k-1 decode.
- Boundary confirmations are true for Qwen3-4B only, no AIME2025 train prompts
  or labels, no task255 reuse, no export/conversion, no endpoint, no promotion,
  no shared deletion, no 30B, no 8-GPU, one GPU, and no training/optimizer
  steps. Worker_3 official mailbox report and PR are still pending.
- Processed worker_3 official closeout mailbox
  `81d56916753645d9b8b14e984869cd9f`: PR #356 is open/base main/CLEAN at head
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`. The eval run source head is
  `87de0a97e6c0406a4b67520faab6b11d91d9131e`; later commits add report/status
  and PR bookkeeping.
- Lead recheck confirms `git diff --check` passes and
  `task285_iter2_same_harness_aime_eval_report.md` matches the artifact evidence
  for FT `12/30 = 0.4` versus base `11/30`. Added PR #356 HOLD comment
  `4601765555`; self-merge waits for task294 independent review of the residual
  sampling semantic-match issue.
