# task176_super_automodel_text2sql_bird_revision_pins_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Pin the two Super AutoModel Text2SQL BIRD notebook `load_dataset`
  training-source examples to PM-provided exact dataset commit revisions.
- Add focused static notebook coverage that parses the notebook JSON and checks
  BIRD/Text2SQL context, pinned train splits, SHA shape, and absence of the
  previous unpinned calls.

## Boundaries

- No notebook execution, live `load_dataset`, HF/dataset download, Text2SQL data
  prep, AutoModel training/eval, endpoint, W&B, cluster, deploy, artifact ops,
  direct `main`/`master` push, or self-merge.
- Scope is limited to the Super AutoModel Text2SQL notebook, focused static
  test, and task/status/report docs.

## Status

- Base: `4077e2e155ec4ed5d3d4594793514e088cae873e`
- Branch: `intern_nem_dev_3/task176_super_automodel_text2sql_bird_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/283
- Checks: focused static notebook pytest, py_compile, Ruff, structured notebook
  probe, unpinned-call grep, added-line live-surface scan, and diff checks
  passed.
- Session 2: stop-hook bookkeeping corrected; PR remains ready for PM gate.
