# task064_pr72_postmerge_review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

PR #72 extended the M1 eval basket from the 8-row v0 basket to the 19-benchmark
full basket. It added the full-basket registry, a combined NeMo Evaluator config,
unified-index integration, tests, and task020 documentation. This task reviews
that PR-sized slice against current `main` and fixes any concrete issue found in
one follow-up PR.

## Goals

1. Review the registry, config, tests, and documentation changed by PR #72.
2. Check consistency with the later eval-basket tooling on current `main`.
3. Patch any correctness or CI-risk issue found.
4. Keep the follow-up scoped to a small PR.

## Acceptance

- [x] PR #72 touched files are reviewed.
- [x] Any concrete bugs found are fixed on this branch.
- [x] Targeted checks cover the fix.
- [x] Registry validation passes.
- [x] Follow-up PR is opened from `intern_nemontron_code_reading/task064_pr72_postmerge_review`.

PR: https://github.com/songCNMS/Nemotron/pull/90

## Review Finding

PR #72 created the `task020_m1_eval_full_basket` task files, but
`history_log.md` and `task_knowledge.md` did not include the expected
`METADATA:SESSION` header. Later sessions appended Session 2 and Session 4
content, so current `main` has useful human-readable task history but no
machine-readable session value for those two files. The task README also still
said Session 4 landed as `PR pending`, even though PR #76 merged as `44c5ec8`.

This task adds `METADATA:SESSION=4` to both task020 files and updates the
Session 4 landing marker to `PR #76 / 44c5ec8`.

## Verification

- `sed` checks confirm both task020 session metadata headers are `METADATA:SESSION=4`.
- `rg "SESSION 4 LANDED: PR #76 / 44c5ec8" workspace/tasks/task020_m1_eval_full_basket/README.md` → pass.
- `PYTHONPATH=src scripts/validate_data_registries.py --quiet` → pass.
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_eval_full_basket.py tests/recipes/super3/test_promotion_gate.py tests/recipes/super3/test_gap_analysis.py` → `52 passed`.
- `git diff --check` → pass.
