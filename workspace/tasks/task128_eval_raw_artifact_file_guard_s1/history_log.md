# task128_eval_raw_artifact_file_guard_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Created branch `intern_nem_dev_3/task128_eval_raw_artifact_file_guard_s1`
  from current `origin/main`
  `22d33bf428bed321c0277badc5d193ada62abf00`.
- Updated `validate_raw_artifact_paths()` to reject local paths that exist but
  are not regular files, while keeping remote artifact refs unchanged.
- Added Qwen eval repro gate and benchmark-alignment tests proving directory
  local raw artifacts fail even with a 64-character SHA entry.
- Verified focused pytest, py_compile, Ruff, structured directory
  raw-artifact probe, and diff checks before staging.
- Opened PR #235 to `main`: https://github.com/songCNMS/Nemotron/pull/235.
