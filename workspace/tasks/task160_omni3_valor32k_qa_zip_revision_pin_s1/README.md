# task160_omni3_valor32k_qa_zip_revision_pin_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_2 -->

Status: Merged
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task160_omni3_valor32k_qa_zip_revision_pin_s1`
Base: `9efec596f0401ab2fbe4909ac54e82be8872ec55`
PR: https://github.com/songCNMS/Nemotron/pull/268 (merged)
Merge commit: `f437b05cd751a2fee36e40fd289f22d0744c0e5c`

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

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/omni3/test_stage0_sft_valor32k_revision_pin.py tests/recipes/omni3/test_stage0_sft_valor_tar_guard.py tests/recipes/omni3/test_stage0_sft_valor32k_config_portability.py` (13 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile src/nemotron/recipes/omni3/stage0_sft/data_prep.py tests/recipes/omni3/test_stage0_sft_valor32k_revision_pin.py`
- PASS: `/work-agents/.venv/bin/ruff check src/nemotron/recipes/omni3/stage0_sft/data_prep.py tests/recipes/omni3/test_stage0_sft_valor32k_revision_pin.py`
- PASS: structured static/AST QA ZIP probe
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
- PASS: added-line live-surface scan showed static revision pin, manifest metadata, tests, and task/status docs only

## Closeout

PM reported PR #268 merged and verified on `main` at
`f437b05cd751a2fee36e40fd289f22d0744c0e5c`. Local `main` was
fast-forwarded to the merge commit. No live Valor32k QA ZIP download,
HF/dataset download, SFT data prep, ffmpeg/audio extraction, train/eval,
endpoint, W&B, cluster, deploy, artifact upload/download, direct
`main`/`master` push, or self-merge occurred.
