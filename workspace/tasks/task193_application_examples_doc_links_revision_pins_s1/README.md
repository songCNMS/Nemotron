# task193_application_examples_doc_links_revision_pins_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Scope

- Pin scoped `docs/application-examples.md` self-repo `use-case-examples`
  GitHub links from `tree/main` to exact revision
  `89a6da531c4c693da585a7cc9ac96c51492bffa4`.
- Add focused static docs test coverage under `tests/docs`.
- Update dev_2 status/task193 docs/report.

## Boundaries

- Static docs/tests/status/task docs only.
- Do not touch deployment guides, Super3 cookbook docs, Omni3 docs,
  task191/task192/task190 files, Nano-Omni files, recipe source files, or
  dev_1/dev_3 task docs.
- No live git clone/fetch/checkout beyond normal repo sync, build/download,
  example execution, recipe/data-prep/train/eval, endpoint, W&B, cluster,
  deploy, artifact operation, direct `main`/`master` push, or self-merge.

## Status

- Base: `89a6da531c4c693da585a7cc9ac96c51492bffa4`
- Branch: `intern_nem_dev_2/task193_application_examples_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/300
- Implementation SHA: `d7ae289d03e03efde244d48a52efd986d89bd5c9`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_application_examples_revision_pins.py`
    -> 1 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_application_examples_revision_pins.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/docs/test_application_examples_revision_pins.py`
    -> passed
  - Structured static probe ->
    `PM_TASK193_APPLICATION_EXAMPLES_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected pinned application-example doc
    URLs only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
