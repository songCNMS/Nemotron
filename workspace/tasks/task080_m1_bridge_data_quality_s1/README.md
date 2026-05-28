# task080_m1_bridge_data_quality_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Background

The M1 RLVR, SWE1, SWE2, and RLHF bridge scripts already produced JSONL
artifacts and lineage manifests, but their bridge outputs did not carry the
same SFT-style source-metadata audit and deterministic output fingerprints
used by the M1 agentic SFT prep path. PR #189 adds that missing bridge audit
surface.

## Scope

- Add shared bridge helpers for source metadata audit, split overlap audit,
  normalized prompt duplicate checks, and SHA-256 output fingerprints.
- Wire `data_quality` and `output_fingerprints` into RLVR, SWE1, SWE2, and
  RLHF bridge manifests and Markdown reports.
- Extend focused bridge tests across the four bridge families.
- Preserve product branch flow: push only
  `intern_nem_dev_1/task080_m1_bridge_data_quality_s1`, open PR to `main`,
  and do not push or merge `main`/`master`.

## Pull Request

- PR: https://github.com/songCNMS/Nemotron/pull/189
- Base branch: `main`
- Head branch: `intern_nem_dev_1/task080_m1_bridge_data_quality_s1`
- Base SHA: `95ddee2f55df4c6d76134f7ea22d5ed5092b6732`
- Implementation head before this docs-only follow-up: `966ae63f42fb77bae650e03aaeb10c348abe5af1`

## Changed Files

- `src/nemotron/recipes/super3/milestones/_bridge_base.py`
- `src/nemotron/recipes/super3/milestones/m1_rlhf/prepare_m1_rlhf_jsonl.py`
- `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py`
- `src/nemotron/recipes/super3/milestones/m1_swe1/prepare_m1_swe1_jsonl.py`
- `src/nemotron/recipes/super3/milestones/m1_swe2/prepare_m1_swe2_jsonl.py`
- `tests/recipes/super3/test_m1_rlhf_data_bridge.py`
- `tests/recipes/super3/test_m1_rlvr_data_bridge.py`
- `tests/recipes/super3/test_m1_swe1_data_bridge.py`
- `tests/recipes/super3/test_m1_swe2_data_bridge.py`
- `workspace/interns/intern_nem_dev_1/status.md`
- `workspace/tasks/task077_data_pipeline_audit_repair_s1/history_log.md`
- `workspace/tasks/task077_data_pipeline_audit_repair_s1/task_knowledge.md`
- `workspace/tasks/task080_m1_bridge_data_quality_s1/README.md`
- `workspace/tasks/task080_m1_bridge_data_quality_s1/history_log.md`
- `workspace/tasks/task080_m1_bridge_data_quality_s1/task_knowledge.md`

## Validation

- `PYTHONPATH=src python -m pytest tests/recipes/super3/test_m1_rlvr_data_bridge.py tests/recipes/super3/test_m1_swe1_data_bridge.py tests/recipes/super3/test_m1_swe2_data_bridge.py tests/recipes/super3/test_m1_rlhf_data_bridge.py`
  passed with 65 tests.
- `git diff --check` passed.
- `python -m ruff check ...` was attempted but Ruff is not installed in this
  environment.

## Residual Risk

- The audit is static and manifest/report-level; it does not inspect generated
  artifacts outside the local bridge outputs.
- Ruff coverage is unavailable until the environment installs `ruff`.
- The docs-only follow-up did not change product code or rerun product tests.

## Main/Master Safety

- No direct push to `main` or `master`.
- No self-merge of PR #189.
