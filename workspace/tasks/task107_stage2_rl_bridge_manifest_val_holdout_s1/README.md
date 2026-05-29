# task107_stage2_rl_bridge_manifest_val_holdout_s1 - Stage2 RL bridge manifest val holdout

<!-- METADATA:STATUS=InReview,ASSIGNEE=intern_nem_dev_2,SESSION=13 -->

## Background

Stage2 RL data-prep defaults for SWE1, SWE2, and RLHF consume M1 bridge
`combined.jsonl` artifacts. The bridge writes train rows first and validation
rows last, with the validation row count recorded in sibling `manifest.json`
under `counts.val`. The previous fixed `val_holdout: 100` default could
mis-split bridge outputs when the real validation count was not 100.

## Goals

- Infer bridge validation holdout from sibling `manifest.json` `counts.val`.
- Validate bridge manifest counts against `combined.jsonl` before splitting.
- Preserve explicit integer `val_holdout` behavior for manual/non-bridge JSONL.
- Update SWE1, SWE2, and RLHF defaults/comments to use manifest inference.
- Add focused tests for inferred holdout, explicit plain JSONL holdout, and
  missing/bad bridge manifests.

## Out Of Scope

- Live data prep, training, eval, endpoint calls, W&B, cluster jobs,
  deployment, direct `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `ac90f15ee5dfbbb9a35ef7f3753581632e1d4d0e`.
- [x] SWE1/SWE2/RLHF defaults use `val_holdout: auto` for bridge combined JSONL.
- [x] `split_local_jsonl()` infers bridge holdout from sibling manifest counts.
- [x] Bad or missing bridge manifests fail clearly in auto mode.
- [x] Explicit integer holdout still works for plain local JSONL.
- [x] Focused pytest, py_compile, Ruff, structured fixture probe, and diff
  whitespace checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/216
