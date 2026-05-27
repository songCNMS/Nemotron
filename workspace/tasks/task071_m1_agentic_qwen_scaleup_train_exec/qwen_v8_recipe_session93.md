# Qwen V8 Clean Final Recipe - Session 93

## Motivation

Session 92 showed two separate hard-math issues after V7:

- AIME25 improved to `63/300`, but 17 unique AIME problems were fully parsed and consistently wrong. This is mostly a reasoning/data issue, not a parser issue.
- HMMT remained in the `13.3%-16.7%` band. Raising HMMT `max_tokens` from `8192` to `12288` increased parsed rows but did not increase exact score.

The data-side fix should reduce ambiguous or noisy solution supervision rather than changing the corrected eval protocol.

## V8 Design

New strategy: `hard_math_clean_final_v8`.

V8 keeps V7 as a separate reproducible strategy and adds stricter hard sidecar filtering:

- Starts from V7 long hard-math trace constraints.
- Requires exactly one `\boxed{...}` expression in the assistant target.
- Requires the boxed payload to be scalar numeric.
- Requires the boxed payload to match the source M0 `expected_answer`.
- Requires only a short non-text tail after the boxed answer.

Implementation details:

- `prepare_m1_agentic_sft.py` now preserves `m0_expected_answer` in math row metadata.
- New helper path: `is_hard_math_clean_final_row`.
- New strategy manifest key: `math_hard_clean_final_v8`.
- `plan_qwen_scaleup_run.py` now emits V8 flags and reports V8 weights.

## Smoke Evidence

Smoke command used existing V7 full M0 cache as both base and sidecar source:

- Base row cap: `10` per environment.
- Math sidecar cap: `5000` per math environment.
- Strategy: `hard_math_clean_final_v8`.

Smoke output:

| Item | Value |
|---|---:|
| Base train rows | 110 |
| Sidecar source math_competition_numeric rows | 5000 |
| Sidecar source math_reasoning_numeric rows | 5000 |
| V8 hard source rows | 29 |
| V8 hard written rows | 29 |
| Conversion errors | 0 |

Smoke artifact:

- `/work-agents/intern_nemontron_code_reading/debug/task071_v8_prep_smoke_session93/manifest.json`

## 30B Script Bundle

Generated bundle:

- `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8`

Key config:

| Field | Value |
|---|---|
| Run name | `task071_qwen30b_a3b_hard_math_clean_final_v8` |
| Strategy | `hard_math_clean_final_v8` |
| Base M0 rows | uncapped |
| Math sidecar source | V7 full M0 cache |
| Pack / seq | `8192 / 8192` |
| Epochs | `0.2` |
| GBS | `8` |
| LR / min LR | `2e-7 / 8e-8` |
| Train entrypoint | `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py` |
| Eval config | `m1_full_basket_launcher_available` |

Scripts:

- Local data prep: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/run_local_data_prep.sh`
- Sync: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/sync_to_nemtron.sh`
- Remote train: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/run_nemtron_train.sh`
- Eval dry run: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/run_eval_basket_dry_run.sh`

## Validation

- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_agentic_sft.py -k "hard_math_clean_final_v8 or hard_math_long_reasoning_v7 or convert_reasoning_record_preserves_reference_solution"` -> `3 passed, 74 deselected`
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py -k "hard_math_clean_final_v8 or hard_math_long_reasoning_v7 or 30b_entrypoint"` -> `3 passed, 11 deselected`
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` -> `90 passed, 1 skipped`
- `ruff check` on changed files -> passed
- `git diff --check` -> passed
