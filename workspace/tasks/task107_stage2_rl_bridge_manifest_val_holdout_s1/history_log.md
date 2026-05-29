# task107_stage2_rl_bridge_manifest_val_holdout_s1 - History Log

<!-- METADATA:SESSION=13 -->

## Session 1 - 2026-05-29

- Received PM assignment to fix Stage2 RL bridge `combined.jsonl`
  validation holdout drift for SWE1, SWE2, and RLHF.
- Fast-forwarded local `main` to `origin/main`
  `ac90f15ee5dfbbb9a35ef7f3753581632e1d4d0e` and created branch
  `intern_nem_dev_2/task107_stage2_rl_bridge_manifest_val_holdout_s1`.
- Added `val_holdout: auto` support to the local RL JSONL split path. Auto mode
  reads sibling `manifest.json`, sums `counts.val`, and validates
  `counts.train + counts.val` against the combined JSONL row count when train
  counts are available.
- Updated SWE1, SWE2, and RLHF data-prep default configs to use manifest
  inference and documented integer overrides for manual/non-bridge inputs.
- Added focused tests for bridge manifest inference with a non-100 validation
  count, explicit plain JSONL holdout, missing manifest failure, and bad
  manifest count failure.
- Verified locally with focused Stage2 RL bridge/data-prep tests, py_compile,
  Ruff, and a structured fixture probe with `counts.val=4`.
