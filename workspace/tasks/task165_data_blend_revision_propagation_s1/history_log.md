# task165_data_blend_revision_propagation_s1 history

<!-- METADATA:SESSION=2 -->

## Session 2 - 2026-05-29

- PM reported PR #273 merged and verified on `main` at merge commit
  `0e190d301348990990650449485aa057eb7405ce`.
- Synced local `main` to `origin/main` at
  `0e190d301348990990650449485aa057eb7405ce`.
- Created closeout branch
  `intern_nem_dev_2/task165_data_blend_revision_propagation_s1_closeout_sync`
  for bookkeeping-only status/task doc updates.
- Recorded task closeout with no active blockers and no live HF/dataset
  download, generic data prep run, train/eval, endpoint, W&B, cluster, deploy,
  artifact upload/download, main/master push, or self-merge.

## Session 1 - 2026-05-29

- Accepted PM assignment and created branch
  `intern_nem_dev_2/task165_data_blend_revision_propagation_s1`.
- Started from assignment base `83ffb47e2e7053ac189b9557011f3a9e6c9ea92c`,
  then refreshed after `origin/main` advanced to
  `83119f9ca83a4978773f4702ef0a4b48c0c4fe94`.
- Added `revision` propagation to pretrain and SFT work items while preserving
  backward-compatible `None` defaults.
- Included each dataset revision, including `None`, in pretrain/SFT deterministic
  run config so the run hash changes when only a source revision changes.
- Passed work-item revisions into pretrain/SFT `DatasetConfig` construction for
  deterministic HF discovery.
- Added revision metadata to `PretrainBlendsArtifact` and `SFTDataArtifact`
  source dataset lineage.
- Added focused offline tests covering setup config, work items, plan adapters,
  run-hash sensitivity, and artifact lineage.
- Verified focused pytest, `py_compile`, Ruff, static revision propagation probe,
  offline AST probe, added-line live-surface scan, and diff checks.
- Opened PR #273 to `main`: https://github.com/songCNMS/Nemotron/pull/273.
