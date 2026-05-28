# task082_qwen_benchmark_artifact_verification_s2 - Qwen artifact verification hardening

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

task079 added the Qwen benchmark alignment ledger, but artifact-check validators
still accepted any non-empty status string. This can let unchecked, unverified,
missing, or arbitrary artifact evidence pass shape validation.

## Goals

- Harden `qwen_eval_repro_gate.py` and `benchmark_alignment.py` so only explicit
  verified artifact-check statuses can validate.
- Keep the allowed set small and compatible with statuses already on `main`:
  `pm_verified` and `local_workspace_verified`.
- Reject `unchecked`, `unverified`, `missing`, and arbitrary status strings.
- Validate ledger `source_manifests` as existing repo-relative files.
- Add focused regression tests.

## Acceptance

- `PYTHONPATH=src python -m pytest -q tests/recipes/super3/test_qwen_eval_repro_gate.py tests/recipes/super3/test_m1_eval_full_basket.py tests/recipes/super3/test_m1_eval_basket.py`
- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_eval_repro_gate.py src/nemotron/recipes/super3/milestones/m1_eval_basket/benchmark_alignment.py`
- `git diff --check`
- PR opened to `main`; no direct push to `main`.
