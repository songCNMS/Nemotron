# task194_nvidia_stack_megatron_core_doc_link_revision_pin_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Pin the Megatron-Core GitHub link in `docs/nemotron/nvidia-stack.md` from
  mutable `main` to exact NVIDIA/Megatron-LM revision
  `6e0d14a68e8defd1e2b65826a1d689b98bfdc62a`.
- Add one focused static docs test under `tests/docs/`.
- Update dev_1 status and this task's docs only.

## Boundaries

- Static docs/test/status only.
- Do not touch `docs/nemotron/super3/quantization.md`, task195,
  application-examples/task193, deployment-guides/task192, Super3
  cookbook/LoRA docs, recipe source files, Nano-Omni, or dev_2/dev_3 docs.
- No live URL probe, build/download/recipe/data-prep, train/eval, endpoint,
  W&B, cluster, deploy, artifact operation, direct `main`/`master` push, or
  self-merge.

## Status

- Base: `a2adec564cace06edf9f1cd91ba174f4aa2429ec`
- Branch:
  `intern_nem_dev_1/task194_nvidia_stack_megatron_core_doc_link_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/302
- Validated implementation head: `c25eb4fe954d606a708177662ac476e67b04e9f1`
- PR state: open, mergeable, merge state `CLEAN`.
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_nvidia_stack_megatron_core_revision_pin.py`
    -> 2 passed.
  - `/work-agents/.venv/bin/python -m py_compile tests/docs/test_nvidia_stack_megatron_core_revision_pin.py`
    -> passed.
  - `/work-agents/.venv/bin/ruff check tests/docs/test_nvidia_stack_megatron_core_revision_pin.py`
    -> passed.
  - Structured static probe -> `STRUCTURED_NVIDIA_STACK_MEGATRON_CORE_PIN_PROBE_PASS`.
  - Product-doc stale mutable Megatron-Core link grep -> no matches.
  - Added-line live-surface scan -> hits limited to static doc URL,
    static test assertions/constants, and task/status docs.
  - `git diff --check` -> passed.
  - `git diff --cached --check` -> passed.
- Blockers: none for PM gate.
- Residual risk: static docs/test-only coverage; no live URL probe, build,
  download, recipe/data-prep, train/eval, endpoint, W&B, cluster, deploy,
  artifact operation, direct `main`/`master` push, or self-merge was performed.
