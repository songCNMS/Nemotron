# task077_data_pipeline_audit_repair_s1 - Task knowledge

<!-- METADATA:SESSION=9 -->

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

---
