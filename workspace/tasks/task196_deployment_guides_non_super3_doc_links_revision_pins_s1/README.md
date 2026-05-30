# task196_deployment_guides_non_super3_doc_links_revision_pins_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Scope

- Pin the remaining non-Super3 self-repo deployment-guide links in
  `docs/deployment-guides.md` from mutable `tree/main` to exact revision
  `a2adec564cace06edf9f1cd91ba174f4aa2429ec`.
- Add one focused docs/static test under `tests/docs`.
- Update dev_2 status/task196 docs/report.

## Boundaries

- Static docs/tests/status/task docs only.
- Do not touch application examples/task193, Super3 cookbook/task192,
  Omni3/task191, nvidia-stack/task194, quantization/task195, recipe source
  files, Nano-Omni notebooks, or dev_1/dev_3 docs.
- No live URL probe, build/download, cookbook/recipe execution,
  data-prep/train/eval, endpoint, W&B, cluster, deploy, artifact operation,
  direct `main`/`master` push, or self-merge.

## Status

- Base: `a2adec564cace06edf9f1cd91ba174f4aa2429ec`
- Branch:
  `intern_nem_dev_2/task196_deployment_guides_non_super3_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/303
- Implementation SHA: `a73ec6b974c6a84d58c2792a1616a68b14d2fa24`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_deployment_guides_non_super3_revision_pins.py`
    -> 1 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_deployment_guides_non_super3_revision_pins.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/docs/test_deployment_guides_non_super3_revision_pins.py`
    -> passed
  - Structured static probe ->
    `PM_TASK196_DEPLOYMENT_GUIDES_NON_SUPER3_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected pinned deployment-guide doc URLs
    and status/task docs only
  - Scoped stale product-doc grep for the three `tree/main` usage-cookbook
    links -> no matches
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
