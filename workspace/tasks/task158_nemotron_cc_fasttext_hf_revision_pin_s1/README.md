# task158_nemotron_cc_fasttext_hf_revision_pin_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

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

- Focused pytest for the static/AST revision-pin test.
- `py_compile` and Ruff on touched product/test files.
- Structured static/AST probe for the revision constant, download keyword, and
  unchanged repo/filename constants.
- `git diff --check` and `git diff --cached --check`.
