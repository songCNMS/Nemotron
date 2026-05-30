# task187_super_grpo_dapo_upstream_doc_links_revision_pins_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Pin mutable NeMo-RL upstream documentation links in the Super GRPO-DAPO
  notebook to revision `bb0a7d43931950a74522e159f7117543a87b580b`.
- Preserve visible `super-v3` branch context prose and the existing pinned
  executable checkout contract.
- Add focused static notebook coverage for pinned docs links and clear touched
  notebook cells.

## Boundaries

- Static notebook/test/status/task docs only.
- Do not touch `docs/nemotron/super3/**`, `src/nemotron/recipes/super3/**`,
  Omni3 docs, or PR #292/#293 files.
- No notebook execution, live git clone/fetch/checkout, build, download,
  recipe/data-prep/train/eval, endpoint, W&B, cluster, deploy, artifact op,
  direct `main`/`master` push, or self-merge.

## Status

- Base: `f74e7c05668f96766d10c730fcd14ddec7191350`
- Branch:
  `intern_nem_dev_3/task187_super_grpo_dapo_upstream_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/294
- Implementation SHA: `5bd77089555a9ce9f2531fa26daf1f541a80941c`
- Tested/merged head: `f2b51ec0c58915b8c1a55bd3de14bc7ed849b12a`
- Merge SHA: `512910a3466012fef675dbcb35b93750e0eba4b4`
- Local main sync: `main` and `origin/main` updated to
  `512910a3466012fef675dbcb35b93750e0eba4b4`.
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/usage_cookbook/test_super_grpo_dapo_rl_checkout_revision.py`
    -> 7 passed
  - `/work-agents/.venv/bin/python -m py_compile tests/usage_cookbook/test_super_grpo_dapo_rl_checkout_revision.py`
    -> passed
  - `/work-agents/.venv/bin/ruff check tests/usage_cookbook/test_super_grpo_dapo_rl_checkout_revision.py`
    -> passed
  - Structured notebook probe ->
    `STRUCTURED_SUPER_GRPO_DAPO_DOC_LINK_PIN_PROBE_PASS`
  - Added-line live-surface scan -> expected notebook static URL/test/task/status
    text only
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
  - PM merged-main verification passed for PR #294.
