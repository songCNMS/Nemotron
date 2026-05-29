# task165_data_blend_revision_propagation_s1

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nem_dev_2 -->

Status: Merged and verified
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task165_data_blend_revision_propagation_s1`
Base: `83119f9ca83a4978773f4702ef0a4b48c0c4fe94`
PR: https://github.com/songCNMS/Nemotron/pull/273 (merged)
Merge Commit: `0e190d301348990990650449485aa057eb7405ce`

## Summary

Thread generic `DataBlend.Dataset.revision` through pretrain and packed-SFT
planning, deterministic run config/hash identity, work items, and artifact
lineage.

## Scope

- `src/nemotron/data_prep/core/work_items.py`
- `src/nemotron/data_prep/recipes/pretrain.py`
- `src/nemotron/data_prep/recipes/sft.py`
- `src/nemotron/kit/artifacts/pretrain_blends.py`
- `src/nemotron/kit/artifacts/sft_data.py`
- Focused offline tests under `tests/data_prep/`
- Task/status docs for `intern_nem_dev_2`

## Boundaries

- No live HF/dataset download, generic pretrain/SFT data prep run, train/eval,
  endpoint call, W&B run, cluster job, deploy, artifact upload/download, direct
  `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/data_prep/test_blend_revision_propagation.py` (6 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile src/nemotron/data_prep/core/work_items.py src/nemotron/data_prep/recipes/pretrain.py src/nemotron/data_prep/recipes/sft.py src/nemotron/kit/artifacts/pretrain_blends.py src/nemotron/kit/artifacts/sft_data.py tests/data_prep/test_blend_revision_propagation.py`
- PASS: `/work-agents/.venv/bin/ruff check src/nemotron/data_prep/core/work_items.py src/nemotron/data_prep/recipes/pretrain.py src/nemotron/data_prep/recipes/sft.py src/nemotron/kit/artifacts/pretrain_blends.py src/nemotron/kit/artifacts/sft_data.py tests/data_prep/test_blend_revision_propagation.py`
- PASS: structured revision propagation static probe
- PASS: offline focused-test AST probe
- PASS: added-line live-surface scan after excluding import reorders
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
