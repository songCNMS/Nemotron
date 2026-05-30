# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-30

- Accepted task198 from PM while Idle.
- Synced local `main` to `origin/main`
  `3d75a20d56ba4931457ca91d0fd8fdfe79b37c21` and created branch
  `intern_nem_dev_1/task198_embed_recipe_upstream_doc_links_revision_pins_s1`.
- Pinned the scoped Export-Deploy tutorial link in
  `src/nemotron/recipes/embed/stage4_export/export.py`.
- Pinned the scoped Automodel biencoder source comment in
  `src/nemotron/recipes/embed/stage2_finetune/biencoder_base.yaml`.
- Added `tests/recipes/embed/test_upstream_doc_links_revision_pins.py` to
  verify both pinned upstream links, stale mutable-link absence, and expected
  Embed context.
- Ran focused pytest, py_compile, Ruff, structured static probe, scoped
  stale-link grep, added-line live-surface scan, `git diff --check`, and
  `git diff --cached --check`.
- Opened PR #305 to `main` at implementation head
  `c7035d4c84eb774f351dc08f9539d829440875c6`.
