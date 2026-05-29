# task171_omni3_rl_docs_source_revision_pins_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Update Omni3 Stage1 RL docs to show the existing runtime `source_revision` pins for MPO, text, and vision RL sources.
- Add focused static docs coverage that reads runtime YAML/JSON configs to prevent docs/config revision drift.
- Keep runtime configs and live-run behavior unchanged.

## Boundaries

- Docs/static-test only.
- No runtime config changes, live HF download, Omni3 data prep, train/eval, endpoint, W&B, cluster, deploy, artifact operations, main push, or self-merge.

## Status

- Base: `9cf231a697ab0decdcbbb890a805c61badbb1529`
- Branch: `intern_nem_dev_1/task171_omni3_rl_docs_source_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/278
- Merge SHA: `e8c748fa834bb62acff2b81d1e26279994b84440`
- Validated implementation head: `663a84d076b8931734e150564d7f1bf643d91f61`
- Checks: focused docs pytest, py_compile, Ruff, structured docs/config probe, added-line live-surface scan, and diff checks passed.
- Merged-main verification: focused Omni3 RL docs revision pytest 3 passed, py_compile, Ruff, diff checks, and structured docs/config probe passed.
