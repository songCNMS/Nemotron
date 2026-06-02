# task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 - history log

<!-- METADATA:SESSION=3 -->

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

## Session 1 - 2026-06-02 UTC - Accepted by worker

- Fetched current `origin/main` at
  `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf` and lead docs branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `ba45e4e0dee345a87e3974e4066c5dc66a57a668`.
- Created worker branch
  `intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1`
  from current `origin/main`.
- Imported task293 docs and began checking whether the corrected AIME2025
  same-harness FT-vs-base comparison can run using the approved task291
  no-export/no-endpoint local generation route.
- Boundaries confirmed: no training or optimizer steps, no AIME2025 train
  prompts/labels, no task255 reuse, no export/conversion, no endpoint, no
  promotion/go-no-go beyond reported gate result, no shared deletion, no main
  push/merge, no 30B, and no 8-GPU.

## Session 2 - 2026-06-02 UTC - refreshed to current main

- Fetched lead follow-up state and updated `origin/main` from
  `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf` to
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a` after #355/task292 merged.
- Rebased worker branch
  `intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1`
  cleanly onto current `origin/main`; refreshed head before this metadata
  commit was `3a4f3f1387d0f82db5d22303f1ceb2820a91a920`.
- Continuing the same task293 scope: run or precisely block corrected AIME2025
  same-harness FT-vs-base eval for task285 iter2, with no training, optimizer
  steps, AIME2025 train prompts/labels, task255 reuse, export/conversion,
  endpoint, promotion, shared deletion, main push/merge, 30B, or 8-GPU.
- Added task-owned no-export/no-endpoint corrected AIME2025 runner at
  `run_no_export_aime_eval.py`, synced the repo plus task247 cache/base
  artifacts to NemTron, and ran task285 iter2 on one H200 with no endpoint or
  export.
- Run `run_20260602T085237Z` completed with `30/30` ok requests, `21/30`
  parsed, `12/30` correct, exact-normalized accuracy `0.4`, and finish reasons
  `stop=21,length=9`.
- Compared against accepted task247 Qwen3-4B base `11/30 =
  0.36666666666666664`; task293 disposition is `PASS` for this eval gate only,
  with no promotion, export, endpoint, 30B, or 8-GPU authorization.

## Session 3 - 2026-06-02 UTC - official closeout packaging

- Lead requested official task293 closeout/PR evidence for eval source head
  `87de0a97e6c0406a4b67520faab6b11d91d9131e` after independent read-only
  confirmation of `run_20260602T085237Z`.
- Packaged the closeout report with command/env, artifact paths, checksum
  manifest, `30` row all-request denominator, same-harness proof, and boundary
  confirmations.
- Recorded the sampling residual risk explicitly: task293 reports
  `sampling_exact_parameter_match=false` because task247 base used SGLang
  `/v1/chat/completions` with `temperature=0.0,top_p=1e-5`, while task293 was
  required to avoid endpoints and therefore used task291 MCore local
  `top_k=1` greedy argmax with `temperature=1.0,top_p=0.0`; deterministic
  greedy semantic intent, prompt tokenization, parser, cache, max tokens, and
  denominator match.
- Boundary confirmation remains unchanged: no export, endpoint, promotion,
  training, AIME2025 train data, shared deletion, main push/merge, 30B, or
  8-GPU.
- Opened PR #356 for the docs/report closeout. Eval run source head remains
  `87de0a97e6c0406a4b67520faab6b11d91d9131e`; report-packaging branch head
  before PR-number bookkeeping was
  `5ace7c74e83cddb8a622775cb70f4d3a5be63fcd`.
