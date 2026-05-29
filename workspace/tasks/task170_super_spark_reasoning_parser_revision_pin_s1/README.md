# task170_super_spark_reasoning_parser_revision_pin_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_2 -->

Status: Complete
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task170_super_spark_reasoning_parser_revision_pin_s1`
Base: `9cf231a697ab0decdcbbb890a805c61badbb1529`
PR: https://github.com/songCNMS/Nemotron/pull/277 (merged)
Merged main: `3c1751adeea4eb26b7e6e8f41f9bb445ebc58f2d`

## Summary

Pin the Spark deployment guide examples that download
`super_v3_reasoning_parser.py` so users do not fetch a drifting Hugging Face
`main` branch file.

## Scope

- `usage-cookbook/Nemotron-3-Super/SparkDeploymentGuide/README.md`
- Focused static docs test under `tests/usage_cookbook/`
- Task/status docs for `intern_nem_dev_2`

## Pin

- Repo: `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4`
- Revision: `4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6`
- File: `super_v3_reasoning_parser.py`

## Boundaries

- Docs/static-test only.
- No live wget/curl, HF/model download, vLLM/TRT-LLM launch, endpoint call,
  W&B run, cluster job, deploy, artifact operation, direct `main`/`master`
  push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_spark_reasoning_parser_revision.py` (3 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_spark_reasoning_parser_revision.py`
- PASS: `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_spark_reasoning_parser_revision.py`
- PASS: structured static probe for exact pinned reasoning-parser URLs and no `raw/main`
- PASS: added-line live-surface scan showed only Spark guide static wget examples
- PASS: `git diff --check`
- PASS: `git diff --cached --check`

## Closeout

- PM reported PR #277 merged and verified on `main` at
  `3c1751adeea4eb26b7e6e8f41f9bb445ebc58f2d`.
- Local `main` was fast-forwarded to the merged `origin/main`.
