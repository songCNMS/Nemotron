# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Started task164 from `origin/main` at `a9b324bf28cd6cb0470b58eec47fd17336fdec0f`.
- Added a default FinePDFs revision pin and config-threaded `load_dataset(..., revision=...)` path.
- Added focused AST/static tests for the repo id, exact revision SHA, config field/default, `load_dataset` revision keyword, and YAML default.
- Ran focused pytest, py_compile, Ruff, structured AST probe, added-line live-surface scan, and `git diff --check` without calling `load_dataset` or running seed generation.
