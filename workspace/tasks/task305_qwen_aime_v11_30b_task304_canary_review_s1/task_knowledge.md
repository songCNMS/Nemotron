# task305_qwen_aime_v11_30b_task304_canary_review_s1 - task knowledge

<!-- METADATA:SESSION=85 -->

## Knowledge Entries

1. Task304 PR #367 is worker_3-owned canary evidence. Lead should not treat it
   as independently accepted until task305 review returns approve/request-
   changes/block.
2. The exact #367 head for review is now
   `a38abd53c897b3c68878abb770cb80f762c20e6f`.
3. The task304 report names evidence source head
   `d8e58461ca1cede2569589f95414c360e0ddd9bc`; reviewers must reconcile the
   later `d8e58461..a38abd53` PR-head delta.
4. Task304 local output root:
   `/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
5. Task304 remote output root:
   `/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
6. Lead artifact observation before assignment found `remote_no_export_canary.rc`
   value `0`, summary disposition `PASS`, `5` prompts, `5` retained
   completions, `5/5` expected-answer matches, `0` empty/mixed-script/
   degeneration counts, and all aggregate/per-rank results and completions at
   5 rows.
7. Task304 remains synthetic non-AIME only. It is not corrected AIME2025/task243
   evidence, not a promotion claim, and not export/endpoint clearance.
8. The task301 `iter_0000035` checkpoint remains a salvage candidate because
   built-in validation did not complete and task301 ended with `train_rc=1`.
9. Corrected AIME2025 same-harness 30B FT-vs-base comparison against base
   `15/30 = 0.5` remains blocked until task304 is accepted through task305 and
   lead creates a separate AIME evaluation task.
10. worker_3 addendum says `773aff2c..a38abd53` is status/history hygiene only.
    Lead observed that range changed only worker_3 status and task304 history,
    with diff-check clean; task305 still must verify this independently.
11. #367 HOLD comment `4605742037` and delivered worker_3/worker_4 peer_sends
    keep #367 unmerged until task305 reports on exact head `a38abd53`.
