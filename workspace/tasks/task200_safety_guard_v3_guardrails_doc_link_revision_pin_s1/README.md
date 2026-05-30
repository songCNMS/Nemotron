# task200_safety_guard_v3_guardrails_doc_link_revision_pin_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

## Scope

- Pin the NeMo Guardrails installation guide link in the Safety Guard V3 NIM
  cookbook from mutable `develop` to Guardrails revision
  `a6fc06f7c3d28b84f3b5c2759ce2366dc8fac5de`.
- Keep the change limited to:
  - `usage-cookbook/Llama-3.1-Nemotron-Safety-Guard-V3/nim_cookbook.ipynb`
  - one focused static notebook test under `tests/usage_cookbook/`
  - dev_3 status and task200 docs.
- Preserve link text, Safety Guard V3/NIM/Guardrails context, and notebook cell
  structure.

## Boundaries

- Static notebook/test/status/task docs only.
- Do not touch task199 SDG long-document files, task198 Embed recipe files,
  task197 Super3 LoRA Text2SQL files, Super3 Stage2 RL README, deployment
  guides/task196, nvidia-stack/task194, quantization/task195, application
  examples, Omni3 docs, Nano-Omni notebooks, recipe source files, or dev_1/dev_2
  docs.
- No notebook execution, live URL probe, Guardrails install, build/download,
  cookbook/recipe execution, data-prep/train/eval, endpoint, W&B, cluster,
  deploy, artifact operation, direct `main`/`master` push, or self-merge.

## Status

- Base SHA: `ea252765464a50d3b2fc46a5ab7922bf8285a6aa`
- Branch:
  `intern_nem_dev_3/task200_safety_guard_v3_guardrails_doc_link_revision_pin_s1`
- PR: Not opened yet
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_safety_guard_v3_guardrails_revision_pin.py`
    -> 3 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_safety_guard_v3_guardrails_revision_pin.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_safety_guard_v3_guardrails_revision_pin.py`
    -> passed
  - Structured static probe ->
    `STRUCTURED_SAFETY_GUARD_V3_GUARDRAILS_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected static notebook/test/status/task
    text only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
