# task173_super_vllm_cookbook_reasoning_parser_revision_pins_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_2 -->

Status: Complete
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task173_super_vllm_cookbook_reasoning_parser_revision_pins_s1`
Base: `e8c748fa834bb62acff2b81d1e26279994b84440`
PR: https://github.com/songCNMS/Nemotron/pull/280 (merged)
Merged main: `5527046f0aeec3e37bf47b7b67f3b1b089164b4f`

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

## Closeout

- PM reported PR #280 squash-merged and verified on `main` at
  `5527046f0aeec3e37bf47b7b67f3b1b089164b4f`.
- Local `main` was fast-forwarded to the merged `origin/main`.
