# task158_nemotron_cc_fasttext_hf_revision_pin_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_2 -->

Status: Merged
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task158_nemotron_cc_fasttext_hf_revision_pin_s1`
Base: `0b31358436c38e698c7c2bc3a89871df273df21c`
PR: https://github.com/songCNMS/Nemotron/pull/265 (merged)
Merge commit: `9efec596f0401ab2fbe4909ac54e82be8872ec55`

## Summary

Pin the Nemotron-CC FastText quality-model `hf_hub_download` call to the
PM-provided Hugging Face commit revision.

## Scope

- `src/nemotron/recipes/data/curation/nemotron-cc/step_3-quality_classification.py`
- Focused static/AST test under `tests/recipes/data/`
- Task/status docs for `intern_nem_dev_2`

## Boundaries

- No live HF download, Nemotron-CC curation run, Ray/Curator pipeline execution,
  train/eval, endpoint, W&B, cluster, deploy, artifact upload/download, direct
  `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/data/test_nemotron_cc_fasttext_revision_pin.py` (1 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile src/nemotron/recipes/data/curation/nemotron-cc/step_3-quality_classification.py tests/recipes/data/test_nemotron_cc_fasttext_revision_pin.py`
- PASS: `/work-agents/.venv/bin/ruff check src/nemotron/recipes/data/curation/nemotron-cc/step_3-quality_classification.py tests/recipes/data/test_nemotron_cc_fasttext_revision_pin.py`
- PASS: structured static/AST probe for the revision constant, download keyword, and unchanged repo/filename constants
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
- PASS: added-line live-surface scan showed static revision pin, static test, and task/status docs only

## Closeout

PM reported PR #265 independently gated, squash-merged, and verified on
`main` at `9efec596f0401ab2fbe4909ac54e82be8872ec55`. Local `main` was
fast-forwarded to the merge commit. No live HF download, Nemotron-CC curation
run, Ray/Curator pipeline execution, train/eval, endpoint, W&B, cluster,
deploy, artifact upload/download, direct `main`/`master` push, or self-merge
occurred.
