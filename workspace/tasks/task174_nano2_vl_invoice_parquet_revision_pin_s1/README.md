# task174_nano2_vl_invoice_parquet_revision_pin_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Pin the Nano2-VL usage cookbook invoice sample parquet URL to the current
  `katanaml-org/invoices-donut-data-v1` commit revision.
- Clear stale notebook output for the touched invoice download cell so no
  floating `resolve/main` invoice URL or signed redirect remains.
- Add focused static notebook JSON coverage.

## Boundaries

- No live `wget`/`curl`, HF/dataset download, notebook execution, Nano2-VL
  inference, endpoint, W&B, cluster, deploy, artifact operations, main push, or
  self-merge.
- Scope is limited to the Nano2-VL notebook, focused static test, and
  task/status docs.

## Status

- Base: `e8c748fa834bb62acff2b81d1e26279994b84440`
- Branch: `intern_nem_dev_1/task174_nano2_vl_invoice_parquet_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/281
- Merge SHA: `4077e2e155ec4ed5d3d4594793514e088cae873e`
- Ready-for-gate head: `cac975d12c4e965dcc665bf808eed315128f59b5`
- Validated implementation head: `eb5502d255955dd23967a989aa43b33683d2d52d`
- Checks: focused notebook pytest, py_compile, Ruff, structured notebook probe, added-line live-surface scan, and diff checks passed.
- Merged-main verification: focused notebook pytest 4 passed, py_compile, Ruff, diff checks, and structured notebook probe passed.
