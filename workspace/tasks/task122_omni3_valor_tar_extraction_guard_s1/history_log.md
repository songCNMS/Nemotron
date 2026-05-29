# task122_omni3_valor_tar_extraction_guard_s1 history

<!-- METADATA:SESSION=20 -->

## Session 20 - 2026-05-29

- Created branch `intern_nem_dev_3/task122_omni3_valor_tar_extraction_guard_s1`
  and rebased it onto current `origin/main`
  `190e8c53c59c08696348b1ae7ca7b58ac4fc8633` after PR #228 merged.
- Replaced the Valor32k `tar xf` subprocess extraction with a guarded Python
  tarfile extractor that validates all members before writing files.
- Preserved canonical `strip_components=4` extraction to top-level
  `videos_dir/*.mp4` files.
- Added synthetic tar tests for benign canonical extraction, absolute path,
  traversal, empty stripped names, symlink, hardlink, special member, and
  pre-existing symlink escape rejection.
- Verified focused Omni3 pytest, py_compile, Ruff, structured tar probe,
  product shellout grep, and `git diff --check` before staging.
- PR: pending.
