# task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1 - history log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-06-02 UTC - assignment

- Created after task293 read-only artifacts showed corrected AIME2025 FT
  `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664`.
- Assigned to worker_5 because #351/task289 was still open but stale for the
  post-task293 state.
- Worker_5 should refresh #351 if clean and scoped, or create a new task295 PR
  and report #351 as superseded.
- Boundaries: docs/provenance only; no training, eval, export, endpoint,
  promotion, task255, AIME2025 train data, shared deletion, 30B, 8-GPU, merge,
  or main push.

## Session 1 - 2026-06-02 UTC - refreshed #351 in place

- Verified #351 was OPEN/base main/MERGEABLE at head
  `ac85acace556f3861576314fc2684733498074f2`, so no superseding task295 PR was
  needed.
- Fetched current `origin/main`
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a` and lead docs
  `70d7aafd0ef4c5073561dcea89cad5fb1d876b6d`.
- Verified #354/task291 and #355/task292 are merged route-pass/review evidence.
- Verified #356/task293 is OPEN/base main/CLEAN/MERGEABLE at exact head
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`.
- Read task293 and task292 reports from their exact remote branch heads.
- Checked for task294 with PR search and branch refs; no task294 review branch
  or PR was visible.
- Updated task289 report/README/history/knowledge, carried task266 runbook
  matrix, worker status, and task295 docs.
- Mirrored the refreshed task289 report to worker_5 outputs with a sha256 file.
- No runtime, training, canary, AIME re-eval, task243 eval, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, shared deletion, merge, main
  push, 30B, 8-GPU, or artifact mutation action was performed.
