# task062_pr70_postmerge_review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

PR #70 added the first M1 eval basket scaffold: an eight-benchmark registry,
schema/index integration, a NeMo Evaluator config, and a regression report
helper. This task reviews that PR-sized slice against current `main` and fixes
any concrete issue found in one follow-up PR.

## Goals

1. Review the runtime code, tests, registry rows, and evaluator config touched
   by PR #70.
2. Exercise focused eval basket tests and registry validation.
3. Patch any correctness or CI-risk issue found.
4. Keep the follow-up scoped to a small PR.

## Acceptance

- [x] PR #70 touched files are reviewed.
- [x] Any concrete bugs found are fixed on this branch.
- [x] Targeted tests cover the fix.
- [x] Registry validation passes.
- [ ] Follow-up PR is opened from `intern_nemontron_code_reading/task062_pr70_postmerge_review`.

## Review Finding

PR #70 introduced `load_eval_results()` for NeMo Evaluator JSON. The function's
error message and docstring require a top-level `tasks` dict, but the
implementation only checked that `tasks` existed. A malformed JSON payload such
as `{"tasks": []}` would pass the loader and fail later in `diff_eval_runs()` on
an unhelpful `.keys()` error.

This task makes the loader reject non-mapping `tasks` values up front and adds a
regression test for that malformed JSON shape.

## Verification

- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_eval_basket.py tests/recipes/super3/test_m1_eval_full_basket.py tests/recipes/super3/test_unified_data_registry.py` → `65 passed`.
- `PYTHONPATH=src scripts/validate_data_registries.py --quiet` → pass.
- `git diff --check` → pass.
