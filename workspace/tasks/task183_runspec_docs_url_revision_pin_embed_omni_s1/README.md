# task183_runspec_docs_url_revision_pin_embed_omni_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

Status: In progress
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task183_runspec_docs_url_revision_pin_embed_omni_s1`
Base: `df45842edade40c19fd0496f3844ef20653a94cc`
Assignment base: `510b6eec33edece3d212a3187b16db3d1b4a8a15`
PR: Pending branch push

## Summary

Pin scoped Embed and Omni3 PEP 723 run-spec `tool.runspec.docs` URLs to the
exact repository commit used as this task base so recipe metadata does not point
at the drifting `main` branch docs.

## Scope

- `src/nemotron/recipes/embed/**` Python run-spec entrypoints containing
  `docs =`.
- `src/nemotron/recipes/omni3/**` Python run-spec entrypoints containing
  `docs =`.
- One focused static test under `tests/`.
- Task/status/report bookkeeping for `intern_nem_dev_2`.

## Pin

- Old URL:
  `https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/main/docs/runspec/v1/spec.md`
- Pinned URL:
  `https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/510b6eec33edece3d212a3187b16db3d1b4a8a15/docs/runspec/v1/spec.md`

## Boundaries

- Static metadata/test/docs only.
- No recipe execution, job submission, data prep, train/eval, endpoint, W&B,
  cluster, deploy, artifact operation, direct `main`/`master` push, or
  self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/test_runspec_docs_url_revision_pin_embed_omni.py` (1 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile` on the focused test and touched Embed/Omni3 recipe entrypoints
- PASS: `/work-agents/.venv/bin/ruff check tests/recipes/test_runspec_docs_url_revision_pin_embed_omni.py`
- PASS: structured static probe for exact scoped pinned docs URLs, no old `/main/` URL, and preserved run-spec markers
- PASS: scoped grep found no old mutable run-spec docs URL in Embed/Omni3 recipe entrypoints
- PASS: added-line live-surface scan; hits are static URL metadata, static tests, and task/status docs only
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
