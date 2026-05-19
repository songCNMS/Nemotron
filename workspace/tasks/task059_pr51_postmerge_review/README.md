# task059_pr51_postmerge_review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

PR #51 (`task058_production_dataset_slug_fixes`) merged the production dataset
metadata fixes for Super3 RL/SFT data prep:

- live Super3 RL blend slug references,
- placeholder target license posture,
- M0 `contamination_against` schema / metadata / manifest propagation,
- competitive programming subset regression tests.

After merge, current `main` advanced with registry validation, license/revision
audits, and sandbox-container work. This task reviews the PR #51 surface against
current `main` and fixes any concrete regressions in a single follow-up PR.

## Goals

1. Review the current code paths touched by PR #51.
2. Re-run focused tests and inspect interactions with later registry tooling.
3. Fix real bugs or CI risks found during review.
4. Keep this follow-up scoped to one PR.

## Acceptance

- [x] PR #51 touched files are reviewed against current `main`.
- [x] Bugs found during review are patched in this task branch.
- [x] Targeted tests cover the patched behavior.
- [x] `tests/recipes/super3` passes or any unrelated failure is documented.
- [x] Follow-up PR is opened from `intern_nemontron_code_reading/task059_pr51_postmerge_review`.

PR: https://github.com/songCNMS/Nemotron/pull/67

## Review Finding

PR #51 introduced two documented contracts with validation that was too loose:

- placeholder target `license` values should be non-empty strings, but a non-string truthy value could pass;
- M0 `contamination_against` is documented as `list[str]`, but runtime and unified-index validation only checked that it was a list.

This task tightens both validators and adds regression tests for runtime M0
registry validation plus unified-index validation.

## Verification

- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m0_data_env.py tests/recipes/super3/test_unified_data_registry.py tests/recipes/super3/test_license_audit.py tests/recipes/super3/test_validate_data_registries_cli.py` → `97 passed, 2 skipped`.
- `PYTHONPATH=src scripts/validate_data_registries.py --quiet` → pass.
- `PYTHONPATH=src scripts/validate_data_registries.py --license-cascade` → pass.
- `PYTHONPATH=src scripts/validate_data_registries.py --check-revision-pins` → pass.
- `PYTHONPATH=src pytest -q tests/recipes/super3` → `349 passed, 5 skipped`.
- `NEMOTRON_RUN_LIVE_HF_TESTS=1 PYTHONPATH=src pytest -q tests/recipes/super3/test_m0_data_env.py -k "live_hf or resolves_on_hf"` → `2 passed, 29 deselected`.
