# task183_runspec_docs_url_revision_pin_embed_omni_s1 history

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-29

- Accepted PM assignment and synced local `main` to `origin/main`
  `510b6eec33edece3d212a3187b16db3d1b4a8a15` with no fast-forward blocker.
- Created branch
  `intern_nem_dev_2/task183_runspec_docs_url_revision_pin_embed_omni_s1`.
- Replaced the mutable `main` run-spec docs URL with the exact
  `510b6eec33edece3d212a3187b16db3d1b4a8a15` URL in scoped Embed and Omni3
  recipe entrypoints only.
- Added focused static coverage for scoped file discovery, exact docs URL pins,
  old URL rejection, and preserved run-spec markers.
- Verified focused pytest, `py_compile`, Ruff, and structured static probe.
- Boundaries preserved: no recipe execution, job submission, data prep,
  train/eval, endpoint, W&B, cluster, deploy, artifact operation,
  `main`/`master` push, or self-merge.

## Session 2 - 2026-05-29

- PM reported PR #288 merged and `main` advanced to
  `df45842edade40c19fd0496f3844ef20653a94cc`.
- Preserved the in-progress task183 diff, rebased branch
  `intern_nem_dev_2/task183_runspec_docs_url_revision_pin_embed_omni_s1` onto
  updated `origin/main` `df45842edade40c19fd0496f3844ef20653a94cc`, and
  reapplied the diff cleanly.
- Kept scope unchanged: Embed/Omni3 run-spec docs URLs still pin to the
  PM-specified docs commit `510b6eec33edece3d212a3187b16db3d1b4a8a15`.
- Reran focused pytest, `py_compile`, Ruff, structured static probe, scoped
  old-URL grep, and added-line live-surface scan on the refreshed base.
- Boundaries preserved: no recipe execution, job submission, data prep,
  train/eval, endpoint, W&B, cluster, deploy, artifact operation,
  `main`/`master` push, or self-merge.
