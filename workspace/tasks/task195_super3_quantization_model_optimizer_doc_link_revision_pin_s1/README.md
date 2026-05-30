# task195_super3_quantization_model_optimizer_doc_link_revision_pin_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

## Scope

- Pin the Model Optimizer PTQ documentation link in
  `docs/nemotron/super3/quantization.md` from mutable `main` to revision
  `40a4dd326d8eed63d3153611201341a32bfab329`.
- Preserve link text and Super3 quantization context.
- Add one focused static docs test for the scoped link pin.

## Boundaries

- Static docs/test/status/task docs only.
- Do not touch `docs/nemotron/nvidia-stack.md`, task194 files, application
  examples/task193, deployment guides/task192, Super3 cookbook/LoRA docs,
  recipe source files, Nano-Omni files, or dev_1/dev_2 docs.
- No live URL probe, build/download, recipe/data-prep/train/eval, endpoint,
  W&B, cluster, deploy, artifact op, direct `main`/`master` push, or
  self-merge.

## Status

- Base: `a2adec564cace06edf9f1cd91ba174f4aa2429ec`
- Branch:
  `intern_nem_dev_3/task195_super3_quantization_model_optimizer_doc_link_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/301
- Implementation SHA: `3a3b1e64c420c3c2bef7ba08cf1cf94aa6f0e003`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_super3_quantization_model_optimizer_revision_pin.py`
    -> 2 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_super3_quantization_model_optimizer_revision_pin.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/docs/test_super3_quantization_model_optimizer_revision_pin.py`
    -> passed
  - Structured static probe ->
    `STRUCTURED_SUPER3_QUANTIZATION_MODEL_OPTIMIZER_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected static docs/test/task/status text
    only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
