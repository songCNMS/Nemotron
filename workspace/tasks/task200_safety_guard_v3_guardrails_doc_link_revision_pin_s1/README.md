# task200_safety_guard_v3_guardrails_doc_link_revision_pin_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

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
- PR: https://github.com/songCNMS/Nemotron/pull/307
- Implementation SHA: `83a91f1e2646b48b1d04dee95318eda017527da5`
- Tested/merged head SHA: `e0b998c75c5ae280562df0b5777cd7ac6a071e79`
- Merge SHA: `85867c86ed9890845e8508afa6cedad837e971f7`
- Local main sync: `origin/main` and `main` updated to
  `85867c86ed9890845e8508afa6cedad837e971f7`
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
  - PM merged-main verification -> focused pytest 3 passed, py_compile, Ruff,
    `git diff --check`, `git diff --cached --check`, scoped stale Guardrails
    develop-link grep, and structured probe
    `PM_MERGED_SAFETY_GUARD_V3_GUARDRAILS_LINK_PIN_PROBE_PASS`
