# task175_nano_omni_mb_cord_v2_dataset_revision_pin_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

Status: In progress
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task175_nano_omni_mb_cord_v2_dataset_revision_pin_s1`
Base: `4077e2e155ec4ed5d3d4594793514e088cae873e`
PR: pending

## Summary

Pin the Nano-Omni Megatron-Bridge CORD-v2 notebook `load_dataset` example so
the training-data preview does not follow a drifting Hugging Face `main` ref.

## Scope

- `usage-cookbook/Nemotron-3-Nano-Omni/Megatron-bridge/mbridge_lora_cord_v2_cookbook.ipynb`
- Focused static notebook test under `tests/usage_cookbook/`
- Task/status docs for `intern_nem_dev_2`

## Pin

- Dataset: `naver-clova-ix/cord-v2`
- Revision: `7f0115a4b758a71d6473b8d085751692da2fef98`

## Boundaries

- Notebook/docs/static-test only.
- No notebook execution, live `load_dataset`, HF/dataset download,
  Megatron-Bridge training, endpoint, W&B, cluster, deploy, artifact
  operation, direct `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_nano_omni_mb_cord_v2_revision.py` (3 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_nano_omni_mb_cord_v2_revision.py`
- PASS: `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_nano_omni_mb_cord_v2_revision.py`
- PASS: structured static notebook probe for exact CORD-v2 repo/revision and no unpinned train example
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
