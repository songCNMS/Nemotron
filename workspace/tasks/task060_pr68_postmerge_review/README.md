# task060_pr68_postmerge_review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

PR #68 (`task030 Session 7 / task058 follow-up`) added semantic auditing for
`contamination_against` metadata after PR #51 / PR #67 tightened the M0 metadata
shape. This task reviews that PR-sized slice against current `main` and fixes
any concrete bugs found in one follow-up PR.

## Goals

1. Review the code and tests introduced by PR #68.
2. Exercise the contamination audit CLI and related registry validation.
3. Patch any correctness or CI-risk issues found.
4. Keep this review/fix scoped to a single PR.

## Acceptance

- [x] PR #68 touched files are reviewed.
- [x] Any concrete bugs found are fixed on this branch.
- [x] Targeted tests cover the fix.
- [x] `tests/recipes/super3` passes or unrelated failures are documented.
- [x] Follow-up PR is opened from `intern_nemontron_code_reading/task060_pr68_postmerge_review`.

PR: https://github.com/songCNMS/Nemotron/pull/86

## Review Finding

PR #68 added `is_placeholder_entry()` for contamination audit sentinel detection.
The implementation used substring matching even though the inline comment said
real eval names such as `Pending-Eval-2026` should not be flagged. The test also
encoded the substring behavior, so a real eval family name containing `pending`
would create a false informational finding.

This task changes sentinel detection to delimiter-aware matching:

- exact sentinel entries still match (`TBD`, `pending`, `none`);
- explanatory placeholder notes still match (`TBD: AIME`, `FIXME later`);
- hyphenated eval names no longer match (`Pending-Eval-2026`, `TBD-Eval-2026`).

## Verification

- `PYTHONPATH=src pytest -q tests/recipes/super3/test_contamination_audit.py tests/recipes/super3/test_validate_data_registries_cli.py tests/recipes/super3/test_unified_data_registry.py` → `81 passed`.
- `PYTHONPATH=src scripts/validate_data_registries.py --check-contamination` → pass.
- `PYTHONPATH=src scripts/validate_data_registries.py --quiet` → pass.
- `PYTHONPATH=src pytest -q tests/recipes/super3` → `548 passed, 5 skipped`.
