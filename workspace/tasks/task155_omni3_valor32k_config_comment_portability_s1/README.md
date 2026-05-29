# task155_omni3_valor32k_config_comment_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

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

- Focused pytest for the Omni3 static test.
- `py_compile` and Ruff on touched test files.
- Scoped grep over `valor32k.yaml`.
- `git diff --check` and `git diff --cached --check`.
