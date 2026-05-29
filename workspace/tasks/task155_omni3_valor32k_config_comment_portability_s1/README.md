# task155_omni3_valor32k_config_comment_portability_s1

<!-- METADATA:STATUS=ReadyForGate,ASSIGNEE=intern_nem_dev_2 -->

Status: Ready for PM gate
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task155_omni3_valor32k_config_comment_portability_s1`
Base: `795eb92359257ed82816a8685db0f9cae1c751ae`
PR: https://github.com/songCNMS/Nemotron/pull/262

## Summary

Replace the scoped Omni3 Valor32k runnable config comment that names a DFW
internal user path with neutral operator guidance to set
`OMNI3_VALOR32K_ENERGON_PATH`.

## Scope

- `src/nemotron/recipes/omni3/stage0_sft/config/valor32k.yaml` comments only.
- Focused static Omni3 test for Valor32k config portability.
- Task/status docs for `intern_nem_dev_2`.

## Boundaries

- Do not change runtime defaults or dataset semantics.
- No live Valor32k/HF download, data prep, train/eval, endpoint, W&B, cluster,
  deploy, artifact download, direct `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/omni3/test_stage0_sft_valor32k_config_portability.py` (1 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile tests/recipes/omni3/test_stage0_sft_valor32k_config_portability.py`
- PASS: `/work-agents/.venv/bin/ruff check tests/recipes/omni3/test_stage0_sft_valor32k_config_portability.py`
- PASS: scoped grep over `valor32k.yaml` found no named-user Lustre path and preserved `OMNI3_VALOR32K_ENERGON_PATH`
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
