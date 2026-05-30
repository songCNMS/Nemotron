# task192_super3_cookbook_index_doc_links_revision_pins_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

## Scope

- Pin scoped self-repo `main` links in the Super3 cookbook index and
  deployment guide cards to revision
  `89a6da531c4c693da585a7cc9ac96c51492bffa4`.
- Preserve visible Super3 product/path context in link text and prose.
- Add focused static docs coverage for the scoped link pins.

## Boundaries

- Static docs/test/status/task docs only.
- Scope is limited to `usage-cookbook/Nemotron-3-Super/README.md`,
  `docs/deployment-guides.md` entries under
  `usage-cookbook/Nemotron-3-Super`, focused test docs, and dev_3 status/task
  docs.
- Do not touch Omni3 docs, task191 files, task190 files, Nano-Omni files, app
  examples, Super3 `evaluate.md`, Super3 recipe source files, or dev_1/dev_2
  task docs.
- No live git clone/fetch/checkout beyond normal repo sync, build/download,
  cookbook execution, recipe/data-prep/train/eval, endpoint, W&B, cluster,
  deploy, artifact op, direct `main`/`master` push, or self-merge.

## Status

- Base: `89a6da531c4c693da585a7cc9ac96c51492bffa4`
- Branch:
  `intern_nem_dev_3/task192_super3_cookbook_index_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/299
- Implementation SHA: `842dc3e91a06e346b4aab1f80b0ffb90e8226e83`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_super3_cookbook_index_doc_links_revision_pins.py`
    -> 4 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_super3_cookbook_index_doc_links_revision_pins.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/docs/test_super3_cookbook_index_doc_links_revision_pins.py`
    -> passed
  - Structured static probe ->
    `STRUCTURED_SUPER3_COOKBOOK_INDEX_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected static docs/test/task/status text
    only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
