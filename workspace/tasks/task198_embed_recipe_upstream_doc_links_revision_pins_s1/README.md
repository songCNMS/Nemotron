# task198_embed_recipe_upstream_doc_links_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Pin the Export-Deploy tutorial link in
  `src/nemotron/recipes/embed/stage4_export/export.py` to revision
  `e025bcd888d92ae226cccd4556f0a790bf714ec7`.
- Pin the Automodel biencoder source comment in
  `src/nemotron/recipes/embed/stage2_finetune/biencoder_base.yaml` to
  revision `7dc827ca9108b2e45eb3beaba8a3cd148bfc658f`.
- Add one focused static test under `tests/recipes/embed/`.
- Update dev_1 status and this task's docs only.

## Boundaries

- Static source/comment/test only.
- Do not touch deployment guides/task196, Super3 LoRA Text2SQL/task197,
  task194 NVIDIA stack, task195 quantization, application examples, Omni3,
  Nano-Omni, unrelated recipe files, or dev_2/dev_3 docs.
- No live URL probe, build/download, recipe execution, data-prep/train/eval,
  endpoint, W&B, cluster, deploy, artifact operation, direct `main`/`master`
  push, or self-merge.

## Status

- Base: `3d75a20d56ba4931457ca91d0fd8fdfe79b37c21`
- Branch: `intern_nem_dev_1/task198_embed_recipe_upstream_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/305
- Validated implementation head: `c7035d4c84eb774f351dc08f9539d829440875c6`
- PR state: open, mergeable, merge state `CLEAN`.
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/embed/test_upstream_doc_links_revision_pins.py`
    -> 2 passed.
  - `/work-agents/.venv/bin/python -m py_compile tests/recipes/embed/test_upstream_doc_links_revision_pins.py src/nemotron/recipes/embed/stage4_export/export.py`
    -> passed.
  - `/work-agents/.venv/bin/ruff check tests/recipes/embed/test_upstream_doc_links_revision_pins.py src/nemotron/recipes/embed/stage4_export/export.py`
    -> passed.
  - Structured static probe -> `STRUCTURED_EMBED_UPSTREAM_DOC_LINK_PIN_PROBE_PASS`.
  - Scoped stale mutable `blob/main` link grep -> no matches.
  - Added-line live-surface scan -> hits limited to static upstream URLs,
    Embed config/default paths, lint formatting in `export.py`, and task/status
    docs.
  - `git diff --check` -> passed.
  - `git diff --cached --check` -> passed.
- Blockers: none for PM gate.
- Residual risk: static source/comment/test-only coverage; no live URL probe,
  build/download, recipe execution, data-prep/train/eval, endpoint, W&B,
  cluster, deploy, artifact operation, direct `main`/`master` push, or
  self-merge was performed.
