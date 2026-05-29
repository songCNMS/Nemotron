# task153_super3_m0_data_env_docs_path_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Make the Super3 M0 data-env README examples portable by replacing scoped
named-user `/mnt/3fs/data/lei.song/nemotron` paths with
`${NEMO_RUN_DIR:-.}/output/super3/...` examples and adding a focused static
test guard.

## Scope

- `src/nemotron/recipes/super3/milestones/m0_data_env/README.md`
- Focused static docs test under `tests/recipes/super3/`
- Task/status docs for `intern_nem_dev_3`

## Boundaries

- No live M0 data prep, HF/dataset download, health baseline run, train/eval,
  endpoint calls, W&B, cluster jobs, deploy, artifact download, direct
  `main`/`master` push, or self-merge.
- Do not touch task150/task152 files, Stage1 SFT docs/config comments, tiny
  blend files, production data-prep logic, generated artifacts, live-run
  reports, or benchmark/eval configs.

## Acceptance Checks

- Focused pytest for the M0 data-env docs guard.
- `py_compile` and Ruff on touched test files.
- Scoped static grep proving the README no longer contains
  `/mnt/3fs/data/lei.song/nemotron`.
- `git diff --check` and `git diff --cached --check`.
- Added-line live-surface scan limited to docs/static-test examples.
