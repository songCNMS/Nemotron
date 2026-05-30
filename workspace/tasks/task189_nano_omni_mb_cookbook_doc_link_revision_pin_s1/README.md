# task189_nano_omni_mb_cookbook_doc_link_revision_pin_s1

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Pin the Nano-Omni Megatron-Bridge cookbook examples link from the mutable
  `nemotron_3_omni` branch URL to revision
  `648756cb99eed872d9e577243495840b9395a6f7`.
- Preserve visible `nemotron_3_omni` branch-context prose and the existing
  executable checkout revision contract.
- Add focused static notebook coverage for the pinned examples link and clear
  touched notebook cells.

## Boundaries

- Static notebook/test/status/task docs only.
- Do not touch PR #295 Nano-Omni GRPO files, Omni3 public docs, Super3 files,
  dev_1/dev_2 task docs, or PR #293/#295 paths outside this scope.
- No notebook execution, live git clone/fetch/checkout beyond normal repo sync,
  build, download, recipe/data-prep/train/eval, endpoint, W&B, cluster, deploy,
  artifact op, direct `main`/`master` push, or self-merge.

## Status

- Original base: `75a994bc2f12f5e5084d2f234a0aca7989fa0ccb`
- Replacement base: `a1878fa7e48eb43ba1d467fa93c064b41333c01e`
- Branch:
  `intern_nem_dev_3/task189_nano_omni_mb_cookbook_doc_link_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/296
- Rebased implementation SHA: `108d654b907c094114a89f7df2d55bfbb3d1e540`
- Rebased pre-docs head: `f5f5308100117af01e9ba36ead8a2a07450aa345`
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_nano_omni_megatron_bridge_checkout_revision.py`
    -> 6 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_nano_omni_megatron_bridge_checkout_revision.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_nano_omni_megatron_bridge_checkout_revision.py`
    -> passed
  - Structured notebook probe -> `STRUCTURED_NANO_OMNI_MB_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected notebook static URL/test/task/status
    text only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
  - Replacement-base rerun on `a1878fa7e48eb43ba1d467fa93c064b41333c01e`
    passed the same focused checks.
