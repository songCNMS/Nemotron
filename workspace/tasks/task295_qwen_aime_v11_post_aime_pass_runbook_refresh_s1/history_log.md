# task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1 - history log

<!-- METADATA:SESSION=1 -->

## Session 76 - 2026-06-02 UTC - assignment

- Created after task293 read-only artifacts showed corrected AIME2025 FT
  `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664`.
- Assigned to worker_5 because #351/task289 is still open but stale for the
  post-task293 state.
- Worker_5 should refresh #351 if clean and scoped, or create a new task295 PR
  and report #351 as superseded.
- Boundaries: docs/provenance only; no training, eval, export, endpoint,
  promotion, task255, AIME2025 train data, shared deletion, 30B, 8-GPU, merge,
  or main push.
- Observed #351 refreshed to head `6d4b6ac6ab54ef09610c6e6bb49b8ebb4acc0a1c`
  and still open/base main/CLEAN/MERGEABLE. The refresh is stale because it
  records #356 as open and task294 as not visible/pending, while current state
  has #357 merged at `24268157...` and #356 merged at `31a3e962...`.
- Added #351 request-changes/HOLD comment `4601906134` and sent worker_5 a
  delivered follow-up to refresh against current main `31a3e962...`. #351 must
  not self-merge until refreshed and lead-gated again.
