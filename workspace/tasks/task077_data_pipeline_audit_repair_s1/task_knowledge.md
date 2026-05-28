# task077_data_pipeline_audit_repair_s1 - Task knowledge

<!-- METADATA:SESSION=12 -->

> **Writing rule**: one line each, format `N. category: content`
>
> Categories: supervisor request, technical fact, file change, test evidence, blocker

---

## Knowledge entries

1. supervisor request: PM assigned intern_nem_dev_1 to own data processing and Qwen training-data reorg audit/fixes on branch `intern_nem_dev_1/task077_data_pipeline_audit_repair_s1`.
2. technical fact: `agentic_v0.yaml` remains the Super3/Nemotron profile; Qwen target packing now uses `qwen_agentic_v0.yaml` with `target_model_family=qwen`, `config_name=qwen_agentic_v0`, `chat_template=tokenizer`, and thinking disabled.
3. file change: `qwen_chat_contract.py` now validates both packed metadata and Qwen data-prep config dictionaries.
4. file change: `prepare_m1_agentic_sft.py` records `data_quality` and `output_fingerprints` in the M1 manifest/report for source metadata, split overlap, normalized prompt duplicates, and deterministic output hashes.
5. test evidence: Focused Qwen planner/contract, M1 prepare, math decontamination, contamination audit/pipeline, registry contamination validation, py_compile, and `git diff --check` passed locally during Session 1.
6. file change: PR #186 opened against `main` for task077.
7. supervisor request: Task080 recovery instruction asked intern_nem_dev_1 to continue branch `intern_nem_dev_1/task080_m1_bridge_data_quality_s1` from base `95ddee2f55df4c6d76134f7ea22d5ed5092b6732`, push branch, open a PR to `main`, and avoid main/master push or merge.
8. file change: `_bridge_base.py` now provides shared bridge data-quality audit/report helpers and SHA-256 output fingerprint helpers for M1 bridge writers.
9. file change: M1 RLVR, SWE1, SWE2, and RLHF bridge manifests/reports now include `data_quality` and `output_fingerprints`; RLVR fingerprints include `combined_path` in addition to train/val.
10. test evidence: Task080 focused bridge shard passed with 65 tests via `PYTHONPATH=src python -m pytest tests/recipes/super3/test_m1_rlvr_data_bridge.py tests/recipes/super3/test_m1_swe1_data_bridge.py tests/recipes/super3/test_m1_swe2_data_bridge.py tests/recipes/super3/test_m1_rlhf_data_bridge.py`; `git diff --check` passed; Ruff was unavailable.
11. file change: PR #189 opened against `main` for task080 bridge data-quality fingerprints.
12. supervisor request: PM follow-up for PR #189 required docs/lineage-only task080 records, with scope, PR URL, base/head, changed files, validation, residual risk, and no main/master push or merge.
13. file change: Added `workspace/tasks/task080_m1_bridge_data_quality_s1/README.md`, `history_log.md`, and `task_knowledge.md`; product code unchanged in Session 10.
14. supervisor request: PM ruff gate for PR #189 failed on import sorting and unused imports; required a narrow fix on `intern_nem_dev_1/task080_m1_bridge_data_quality_s1` with no main/master push or merge.
15. file change: Session 11 ruff fix is import/lint-only: Ruff-sorted bridge/test imports, removed unused `read_jsonl` bridge imports, and kept `KNOWN_STATUSES` as an explicit bridge-module re-export.
16. test evidence: Exact PM Ruff command passed, focused bridge pytest shard passed with 65 tests, `python -m py_compile` for touched bridge modules/tests passed, and `git diff --check` passed.
17. supervisor request: PM corrected the misdelivered task085/stage3 eval message; intern_nem_dev_1 must work only on task086 Qwen SFT data-prep default contract.
18. file change: Task086 changes Super3 SFT data-prep runnable defaults (`runspec` default and direct `DEFAULT_CONFIG_PATH`) to `qwen_agentic_v0`, leaving legacy Super3/Nemotron configs available through explicit selection.
19. test evidence: Task086 validation passed with the Qwen contract test, required Qwen/SFT pytest shard, py_compile, Ruff on touched Python files/tests, and `git diff --check`.
20. file change: PR #192 opened against `main` for task086 Qwen SFT data-prep default contract.

---
