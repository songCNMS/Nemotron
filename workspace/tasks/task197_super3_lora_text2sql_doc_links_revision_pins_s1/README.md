# task197_super3_lora_text2sql_doc_links_revision_pins_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Pin scoped Super3 LoRA Text2SQL self-repo doc links from mutable `main` to
  Nemotron revision `3d75a20d56ba4931457ca91d0fd8fdfe79b37c21`.
- Keep the change limited to:
  - `usage-cookbook/Nemotron-3-Super/lora-text2sql/README.md`
  - `usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/mbridge_lora_cookbook.ipynb`
  - one focused static docs/notebook test
  - dev_3 status and task197 docs.
- Preserve link text, recipe names, and Super3 LoRA Text2SQL context.

## Boundaries

- Static docs/notebook/test/status/task docs only.
- Do not touch task196 deployment guides, task194 nvidia-stack, task195
  quantization, application examples, Omni3, Nano-Omni, recipe source files, or
  dev_1/dev_2 docs.
- No notebook execution, live URL probe, build/download, cookbook/recipe
  execution, data-prep/train/eval, endpoint, W&B, cluster, deploy, artifact
  operations, direct `main`/`master` push, or self-merge.

## Status

- Base SHA: `3d75a20d56ba4931457ca91d0fd8fdfe79b37c21`
- Branch:
  `intern_nem_dev_3/task197_super3_lora_text2sql_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/304
- Implementation SHA: `5ec3f6d9fa72f59f03f4d7b2a52d50680b93943a`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_super3_lora_text2sql_doc_links_revision_pins.py`
    -> 3 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_super3_lora_text2sql_doc_links_revision_pins.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_super3_lora_text2sql_doc_links_revision_pins.py`
    -> passed
  - Structured static probe ->
    `STRUCTURED_SUPER3_LORA_TEXT2SQL_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected static docs/notebook/test/status/task
    text only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
