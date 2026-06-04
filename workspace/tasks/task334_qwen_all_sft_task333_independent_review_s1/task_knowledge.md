# task334_qwen_all_sft_task333_independent_review_s1 - task knowledge

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=85 -->

1. #396/task333 head `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e` is the only
   review target. If the PR head changes, stop and report head drift.
2. Lead-side precheck observed task333 root `run_20260604T074500Z` with
   disposition `PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW`, 96 shards,
   89,325 rows, 342,875,996 input tokens, 38,245,535 supervised tokens,
   artifact and packed shard checksum rc 0, Qwen3-30B contract rc 0, and no
   broken split symlinks.
3. Residuals to inspect rather than hide: no fresh task333 decontam scan,
   task299 lacks normalized-prompt field, hard-math seed source has valid/test
   zero-row shards, and SWE still truncates to 4096 while retaining nonzero
   supervised tokens.
4. Approval would only support docs/evidence closeout and a later lead-gated
   training-preflight task. It must not release task310, training, eval, export,
   endpoint, promotion, or 30B scale by itself.
5. #397 head `8a7ca3e8898514bbb1b56ed9996edfc35b4be617` documents
   `REQUEST_CHANGES_REPORT_ARTIFACT_MISMATCH` for old #396 head
   `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`.
6. #396 refreshed head `9a9471e35e3d80f6bf2995478ddf4bd1ef785a66` must receive
   a refreshed task334 review. The expected delta is worker_1 status plus
   task333 report hash correction only; the artifact root remains
   `run_20260604T074500Z`.
7. #396 advanced again to `6261daaa37172caa11929b0b88f685b63f987221`.
   Lead verified `9a9471e3..6261daaa` is worker_1 status plus task333
   history/task_knowledge metadata only. Current task334 target is exact head
   `6261daaa`.
8. #397/task334 exact head `79c8a0f3751f862491517f5c472c26da35e2a7dc` is
   lead-approved for worker_4 self-merge by comment `issuecomment-4620405875`.
   It remains docs/evidence closeout only; it does not release task310 or any
   training/eval/export/endpoint/promotion/30B action.
9. #397 merged at `2026-06-04T08:33:14Z` via merge commit
   `35b6d649cf15eddf09978628f60522b9416607af`. It is the independent review
   evidence supporting #396 docs closeout at exact head `6261daaa`.
