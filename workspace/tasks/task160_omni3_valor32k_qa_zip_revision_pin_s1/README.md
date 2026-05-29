# task160_omni3_valor32k_qa_zip_revision_pin_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Summary

Pin the Omni3 Valor32k QA ZIP default URL to the PM-provided upstream commit
instead of the floating `refs/heads/main` ref.

## Scope

- `src/nemotron/recipes/omni3/stage0_sft/data_prep.py`
- Focused static/AST Valor32k tests under `tests/recipes/omni3/`
- Task/status docs for `intern_nem_dev_2`

## Boundaries

- No live Valor32k QA ZIP download, HF/dataset download, SFT data prep,
  ffmpeg/audio extraction, train/eval, endpoint, W&B, cluster, deploy,
  artifact upload/download, direct `main`/`master` push, or self-merge.

## Acceptance Checks

- Focused pytest for new/nearby Valor32k tests.
- `py_compile` and Ruff on touched product/test files.
- Static grep/probe proving no `refs/heads/main` remains in the product
  Valor32k QA URL path.
- Added-line live-surface scan.
- `git diff --check` and `git diff --cached --check`.
