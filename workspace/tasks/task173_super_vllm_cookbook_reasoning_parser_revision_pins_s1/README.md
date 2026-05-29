# task173_super_vllm_cookbook_reasoning_parser_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

Status: In progress
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task173_super_vllm_cookbook_reasoning_parser_revision_pins_s1`
Base: `3c1751adeea4eb26b7e6e8f41f9bb445ebc58f2d`
PR: pending

## Summary

Pin the vLLM cookbook `super_v3_reasoning_parser.py` download examples so
BF16, FP8, and NVFP4 users do not fetch a drifting Hugging Face `main` file.

## Scope

- `usage-cookbook/Nemotron-3-Super/vllm_cookbook.ipynb`
- Focused static notebook test under `tests/usage_cookbook/`
- Task/status docs for `intern_nem_dev_2`

## Pins

- BF16: `d51eab0d1f979ebc26b546e634a04f450d99158e`
- FP8: `7d7e5797b8a3c7abbab54033b6004e93e8b6bc91`
- NVFP4: `4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6`

## Boundaries

- Notebook/docs/static-test only.
- No live wget/curl, HF/model download, vLLM/TRT serving launch, endpoint
  call, W&B run, cluster job, deploy, artifact operation, direct
  `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_vllm_cookbook_reasoning_parser_revision.py` (3 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_vllm_cookbook_reasoning_parser_revision.py`
- PASS: `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_vllm_cookbook_reasoning_parser_revision.py`
- PASS: structured notebook probe for exact BF16/FP8/NVFP4 parser URLs and no floating main parser URL
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
