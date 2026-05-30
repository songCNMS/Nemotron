# task190_super3_evaluate_evaluator_doc_link_revision_pin_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_2,SESSION=2 -->

## Scope

- Pin NeMo Evaluator reproducibility guide links in
  `docs/nemotron/super3/evaluate.md` from mutable `blob/main` to exact revision
  `eb3ddf2acc7f2e1fa03aeba168afea636562779c`.
- Add focused docs/static test coverage under `tests/docs`.
- Update intern status/task docs/report.

## Boundaries

- Static docs/tests/status/task docs only.
- Do not touch Nano-Omni PR #295 files, task189 files, Omni3 docs, or other
  Super3 docs.
- No live eval, evaluator launch, endpoint call, W&B, cluster, deploy, artifact
  operation, live git clone/fetch/checkout beyond normal repo sync, direct
  `main`/`master` push, or self-merge.

## Status

- Base: `a1878fa7e48eb43ba1d467fa93c064b41333c01e`
- Original assignment base: `75a994bc2f12f5e5084d2f234a0aca7989fa0ccb`
- Branch:
  `intern_nem_dev_2/task190_super3_evaluate_evaluator_doc_link_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/297
- Implementation SHA: `40df6c7a7a72278389a3ca6c66453cbe671750bc`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_super3_evaluate_evaluator_revision_pin.py`
    -> 1 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_super3_evaluate_evaluator_revision_pin.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/docs/test_super3_evaluate_evaluator_revision_pin.py`
    -> passed
  - Structured static probe ->
    `PM_TASK190_SUPER3_EVALUATE_EVALUATOR_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected static docs/test/status/task text
    only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
