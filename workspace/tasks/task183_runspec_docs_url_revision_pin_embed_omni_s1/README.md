# task183_runspec_docs_url_revision_pin_embed_omni_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_2 -->

Status: Complete
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task183_runspec_docs_url_revision_pin_embed_omni_s1`
Base: `df45842edade40c19fd0496f3844ef20653a94cc`
Assignment base: `510b6eec33edece3d212a3187b16db3d1b4a8a15`
Replacement tested base: `90b3122c5b803ed0192ac0dab273473da6a3c52f`
PR: https://github.com/songCNMS/Nemotron/pull/290 (merged)
PR head: `a5cc62bda8bc2aafaf83fadc85937f21a2ebddd4`
Merged main: `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa`

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

## Closeout

- PM reported PR #290 merged and verified on `main`
  `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa`.
- Tested replacement base/head were
  `90b3122c5b803ed0192ac0dab273473da6a3c52f` /
  `a5cc62bda8bc2aafaf83fadc85937f21a2ebddd4`.
- Merged-main verification passed focused Embed/Omni run-spec pytest,
  `py_compile` on touched recipe/test files, focused Ruff, diff checks, and
  `PM_MERGED_RUNSPEC_EMBED_OMNI_DOCS_URL_PROBE_PASS`.
- Local `main` was synced to merged `origin/main`, and closeout bookkeeping was
  recorded on branch
  `intern_nem_dev_2/task183_runspec_docs_url_revision_pin_embed_omni_s1_closeout_sync`.
- No active task remains; status is Idle / Current Task None.
- No recipe execution, job submission, data prep, train/eval, endpoint, W&B,
  cluster, deploy, artifact operation, direct `main`/`master` push, or
  self-merge was performed for closeout.
