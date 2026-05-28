# task085_stage3_eval_defaults_normalization_s1 - Stage3 eval defaults normalization

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

`load_stage3_eval_config()` expands compact stage3 eval overlays such as
`m1_basket`, `m1_full_basket`, `m1_full_basket_launcher_available`, and
`m1_corrected_math_comparison`. After normalization, the launcher-facing config
still retained top-level `defaults` metadata inherited from
`stage3_eval/config/default.yaml`.

## Goals

- Strip top-level `defaults` from normalized evaluator launcher configs.
- Preserve compact basket task expansion into `evaluation.tasks`.
- Preserve Qwen eval `chat_template_kwargs` inherited from default config.
- Keep source YAML audit metadata such as `qwen_chat_contract` available before
  normalization but stripped from launcher configs.

## Out Of Scope

- Live evals, endpoint calls, W&B export, cluster jobs, deployment, or merge.

## Acceptance

- Focused tests cover `default`, `m1_basket`, `m1_full_basket`,
  `m1_full_basket_launcher_available`, and `m1_corrected_math_comparison` after
  `load_stage3_eval_config()` plus `normalize_evaluator_launcher_config()`.
- Required eval pytest shard passes.
- `python -m py_compile` passes for touched Python files/tests.
- `/work-agents/.venv/bin/ruff check` passes for touched Python files/tests when
  available.
- `git diff --check` and `git diff --cached --check` pass.
