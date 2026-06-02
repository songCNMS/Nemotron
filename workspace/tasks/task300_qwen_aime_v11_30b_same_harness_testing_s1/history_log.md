# task300_qwen_aime_v11_30b_same_harness_testing_s1 - history log

<!-- METADATA:SESSION=5 -->

## Session 76 - 2026-06-02 UTC - assignment

- Created by `intern_nemotron_lead` as the 30B same-harness testing gate.
- Assigned to `intern_nemotron_worker_3`.
- First required measurable gate is the 30B same-harness base AIME2025 score;
  FT cannot be judged without it.

## Session 1 - 2026-06-02 UTC - accepted by worker

- Fetched `origin/main` at
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7` and lead docs branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `676d8556`.
- Created worker branch
  `intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1`
  from current `origin/main` and imported task300 docs.
- Scope accepted: establish exact same-harness 30B base AIME2025 score first;
  after task301 checkpoint exists, run non-AIME canary before any corrected
  AIME2025 FT-vs-base comparison.
- Boundaries confirmed: no training, optimizer steps, task255 reuse, AIME2025
  train prompts/labels, shared deletion, promotion, main push/merge, or
  production endpoint.
- Inspected fetched task298/task299/task301/task302 branches and visible output
  roots. task298 has no runtime/resource/base-load report or artifacts visible;
  task299 has no data/packing report visible; task301 PR #362 reports
  `BLOCKED_UPSTREAM_GATES_MISSING` and no checkpoint; task302 remains HOLD.
- Ran read-only NemTron probes under
  `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T144005Z`.
  Candidate 30B model path exists and eight H200s were idle, but no local
  endpoint was listening and no task298 route proof exists.
- Wrote `30b_base_aime2025_report.md` with disposition
  `BLOCK_UPSTREAM_TASK298_ROUTE_MISSING`. No base completions, parser
  diagnostics, numerator, denominator, or score were produced.
- Opened PR #363 for the task300 blocked base-gate report at branch head
  `d0b6e46e`.

## Session 2 - 2026-06-02 UTC - blocker report publication

- Lead follow-up requested branch/PR or mailbox evidence for the local
  `30b_base_aime2025_report.md` blocker and reiterated not to run 30B base
  AIME until task298 official route PASS is processed.
- Confirmed PR #363 is the task300 blocker PR. Prepared to push PR-number
  bookkeeping plus this Session 2 status update before sending mailbox.
- Boundary state unchanged: no 30B base AIME eval, endpoint, export, training,
  canary, FT judgment, task255 reuse, AIME2025 train data, shared deletion,
  promotion, main push, or merge was run.

## Session 3 - 2026-06-02 UTC - 30B base score produced

- Lead released the 30B same-harness BASE AIME route after task298/#364 route
  approval. PR #364 is merged with approved head
  `8f1f7df9d6499eedb150d7e63323df8ee0411f41` and merge commit
  `a0235f14dc3c49797c507ab4578536ba2d6ed3ac`. Later task299/#365 merged into
  main at `205fc919a643b1478964a9e91793247c5e821a38`.
- Added task-owned endpoint runner
  `run_sglang_base_aime_eval.py` to retain full completions, parser
  diagnostics, endpoint manifest, command/env manifest, and checksums while
  preserving the corrected task071/task247 scoring semantics.
- Launched an eval-only SGLang endpoint on NemTron from
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` with
  `tp=4`, `dp=2`, context length `16384`, served model
  `qwen3-30b-a3b-instruct-2507-base`, and no export/conversion.
- Ran corrected AIME2025 base scoring under
  `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`.
  Eval directory:
  `eval/qwen30b_base_aime2025_30x1_20260602T152351Z`.
- Result: `15/30` exact-normalized base accuracy `0.5`; denominator all 30
  requested rows; `30/30` status ok; parsed `19/30`; finish reasons
  `stop=19`, `length=11`.
- Stopped the eval-only endpoint after the run. Exact post-stop check recorded
  no port `13230` listener and no exact `python3 -m sglang.launch_server`
  process for the task300 endpoint; GPUs returned to `1 MiB`, `0 %`.
- Updated `30b_base_aime2025_report.md` to `BASE_PASS` with commands/env,
  artifact roots, checksums, denominator, full completion and parser diagnostic
  paths, residuals, and boundary confirmations.
- Boundaries maintained: no FT eval, no non-AIME canary, no training or
  optimizer step, no export for promotion, no endpoint promotion, no task255
  reuse, no AIME2025 train data, no shared deletion, no promotion claim, no main
  push, and no merge.

## Session 5 - 2026-06-02 UTC - PR merged

- Lead gate approved self-merge of PR #363 after worker_4 independent review
  approved exact head `155eb0c6845c0bf2b7d40051a9045533ffe00589` with
  residuals.
- Verified PR #363 was `OPEN`, base `main`, `CLEAN`, `MERGEABLE`, non-draft,
  and still at exact head
  `155eb0c6845c0bf2b7d40051a9045533ffe00589` immediately before merge.
- Self-merged PR #363 through GitHub. Merge time:
  `2026-06-02T15:46:29Z`; merge commit:
  `e400cea8a1604bc95cc430a194811ff553b99401`; merged head:
  `155eb0c6845c0bf2b7d40051a9045533ffe00589`.
- Fetched `origin/main` and confirmed it advanced to merge commit
  `e400cea8a1604bc95cc430a194811ff553b99401`.
- No post-merge issue observed.
- Scope remains base comparator evidence only: corrected same-harness 30B base
  score `15/30`, exact-normalized accuracy `0.5`, with full completions,
  parser diagnostics, manifests, and checksums retained under the task300
  artifact root.
- Boundaries maintained after merge: no FT eval, no non-AIME canary, no
  training or optimizer step, no export, no endpoint promotion, no task255
  reuse, no AIME2025 train data, no shared deletion, and no promotion action.
