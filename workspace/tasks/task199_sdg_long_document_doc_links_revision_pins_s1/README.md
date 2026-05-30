# task199_sdg_long_document_doc_links_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Scope

- Pin the three SDG long-document self-repo links in
  `docs/nemotron/data/sdg/long-document.md` from mutable `tree/main` to exact
  Nemotron main revision `306b2f1217e000b5972155c1f2b1ba6660c994bd`.
- Add one focused docs/static test under `tests/docs`.
- Update dev_2 status/task199 docs/report.

## Boundaries

- Static docs/tests/status/task docs only.
- Do not touch task197 Super3 LoRA Text2SQL files, task198 Embed recipe files,
  Guardrails notebook, Super3 Stage2 RL README, deployment guides/task196,
  nvidia-stack/task194, quantization/task195, application examples, Omni3 docs,
  Nano-Omni notebooks, unrelated recipe files, or dev_1/dev_3 docs.
- No live URL probe, build/download, recipe execution, SDG data generation,
  data-prep/train/eval, endpoint, W&B, cluster, deploy, artifact operation,
  direct `main`/`master` push, or self-merge.

## Status

- Base: `e690bdac75ae5a85e1a167e3553d631d29732d32`
- Original assignment base: `d926c40f4ea393d42f7bd38a3fbfe84e2ec72815`
- Branch: `intern_nem_dev_2/task199_sdg_long_document_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/306
- Implementation SHA: `9a69561b55e5069bb92552d61a660de95f4a4025`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_sdg_long_document_revision_pins.py`
    -> 1 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_sdg_long_document_revision_pins.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/docs/test_sdg_long_document_revision_pins.py`
    -> passed
  - Structured static probe ->
    `PM_TASK199_SDG_LONG_DOCUMENT_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected pinned SDG long-document doc URLs
    and static test/task docs only
  - Scoped stale product-doc grep for `tree/main` long-document links -> no
    matches
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
