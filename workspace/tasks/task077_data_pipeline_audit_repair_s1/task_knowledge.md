# task077_data_pipeline_audit_repair_s1 - Task knowledge

<!-- METADATA:SESSION=17 -->

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
21. supervisor request: PM assigned task087 to sync latest main, add SWE1/SWE2/RLHF bridge combined outputs, rewire stage2 RL data-prep defaults to bridge combined JSONL paths, run focused bridge/default checks, open a PR to `main`, and avoid live data/cluster/W&B/deploy/main push/merge.
22. technical fact: SWE1/SWE2/RLHF data-prep defaults consume one `input_path`; bridge `combined.jsonl` must preserve the RLVR train+val val-last contract so `_data_prep_base` can re-split without dropping the existing val rows.
23. file change: SWE1/SWE2/RLHF bridge writers now emit `combined.jsonl`, record `combined_path` in manifest/report fingerprints, and add `m1_<mix>_combined_jsonl` lineage outputs.
24. file change: SWE1/SWE2/RLHF stage2 RL data-prep defaults now point at `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_<mix>/combined.jsonl` instead of developer-local `/lustre` release JSONL files.
25. test evidence: Task087 validation passed with the required bridge/RLVR/default pytest shard, py_compile for touched Python files/tests, Ruff on touched Python files/tests, `git diff --check`, and `git diff --cached --check`.
26. file change: PR #194 opened against `main` for task087 stage2 RL bridge data-prep defaults.
27. supervisor request: PM assigned task090 to sync latest main, move Nano3 stage0 pretrain data-prep default output_dir off named-user `/lustre`, add focused static tests, open a PR to `main`, and avoid live data/training/endpoint/W&B/cluster/deploy/main push.
28. technical fact: `PreTrainDataPrepConfig.output_dir` already defaults to `Path(os.environ.get("NEMO_RUN_DIR", ".")) / "output/nano3/stage0_pretrain"`; YAML default should follow that portable contract.
29. file change: Nano3 stage0 pretrain `default.yaml` now uses `${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain` for `output_dir`; `tiny.yaml` remains unchanged.
30. test evidence: Task090 focused Nano3 config pytest shard passed, py_compile passed for the touched test, Ruff passed for the touched test, static output_dir scan found no `/lustre` or `users/mromeijn` output_dir defaults, and diff checks passed.
31. file change: PR #197 opened against `main` for task090 Nano3 stage0 pretrain output portability.
32. supervisor request: PM assigned task092 to sync latest main, fix Nano3 stage2 RL Qwen chat kwargs, stop-string, and parser/plugin contract in `default.yaml` and `tiny.yaml`, add focused tests, open a PR to `main`, and ignore unrelated generic prompt text.
33. file change: Nano3 stage2 RL `default.yaml` and `tiny.yaml` now pin tokenizer and vLLM serving `chat_template_kwargs` to `enable_thinking=false` and `truncate_history_thinking=false`.
34. file change: Nano3 stage2 RL `default.yaml` and `tiny.yaml` now use `stop_strings: ["<|im_end|>"]`, `tool_parser: qwen3_coder`, `reasoning_parser: nano_v3`, and `reasoning_parser_plugin: nemo_rl/utils/nano_v3_reasoning_parser.py`.
35. test evidence: Task092 focused Qwen RL contract pytest passed with 7 tests, py_compile passed for the touched test, Ruff passed for the touched test, structured YAML probe passed, and diff checks passed.
36. blocker: Suggested existing Nano3 stage2 RL integration shard is blocked by unrelated pre-existing drift in `test_data_prep_train_integration.py` imports/APIs and missing legacy helper modules.
37. file change: PR #199 opened against `main` for task092 Nano3 stage2 RL Qwen contract.
38. supervisor request: PM follow-up for active task092 required fixing Nano3 tiny validation split because `validation_jsonl_fpath` reused `${art:data,train}`.
39. file change: Nano3 stage2 RL `tiny.yaml` now uses `train_jsonl_fpath: ${art:data,train}` and `validation_jsonl_fpath: ${art:data,val}`.
40. test evidence: Task092 focused Qwen RL contract pytest now passes with 8 tests and includes a regression proving tiny train/validation artifact split keys differ.
41. file change: PR #199 updated with the Nano3 tiny split follow-up.
42. supervisor request: PM assigned task095 to sync from main at or after `90e64c745e6ed905559aacf11125b4d5d3d1f255`, audit/fix Super3 stage1_rlvr and stage3_rlhf GenRM reasoning parser drift, add focused tests, open a PR, and avoid live runs/main push/self-merge.
43. technical fact: Super3 stage1_rlvr and stage3_rlhf rollout policy HTTP serving was already pinned to `reasoning_parser: nano_v3` with `reasoning_parser_plugin: nemo_rl/utils/nano_v3_reasoning_parser.py`, while GenRM vLLM `server_args` still used stale `deepseek_r1`.
44. file change: Super3 stage1_rlvr and stage3_rlhf GenRM `server_args` now use `nano_v3` plus `nemo_rl/utils/nano_v3_reasoning_parser.py`; non-reasoning judge servers were left unchanged.
45. test evidence: Task095 required Super3 parser/stop-string pytest shard passed with 38 tests using `PYTHONPATH=src`, py_compile passed for the touched test, Ruff passed for the touched test, and diff checks passed.
46. file change: PR #202 opened against `main` for task095 Super3 GenRM reasoning parser contract.
47. supervisor request: PM assigned task098 to sync from main at or after `780626169586fe5be34993deaa49598b7af11a44`, fix Qwen SFT local train packed-dir defaults, add focused tests, open a PR, and avoid main push/self-merge.
48. technical fact: Qwen local train entrypoints reuse `m1_agentic_train.yaml`, whose inherited packed-dir fallback is `../output/super3/stage1_sft_agentic_v0/splits`, while Qwen data prep writes `../output/super3/stage1_sft_agentic_v0_qwen/splits`.
49. file change: `qwen_local_train.py` and `qwen3_30b_a3b_local_train.py` now resolve the inherited legacy packed-dir fallback to the Qwen packed-data default before metadata validation, while preserving explicit `SUPER3_M1_AGENTIC_PACKED_DIR` and config/CLI overrides.
50. test evidence: Task098 requested M1 Agentic SFT/Qwen scale-up pytest shard passed with 107 tests and 1 skipped; py_compile, Ruff, static OmegaConf packed-dir probe, and diff checks passed.
51. file change: PR #205 opened against `main` for task098 Qwen SFT local train packed-dir contract.
52. supervisor request: PM assigned task102 to sync latest main, fix Qwen scale-up planner remote-root portability, preserve explicit `--remote-root`, add focused tests, open a PR, and avoid live runs/main push/self-merge.
53. technical fact: `plan_qwen_scaleup_run.py` previously defaulted `DEFAULT_REMOTE_ROOT` to `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup`, so rendered sync/train scripts could write into another intern workspace.
54. file change: Qwen scale-up planner `DEFAULT_REMOTE_ROOT` now resolves under the current checkout owner's `../outputs/task067_qwen_scaleup_remote` path.
55. test evidence: Task102 focused planner pytest shard passed with 22 tests; py_compile, Ruff, static rendered portability probe, and diff checks passed.
56. file change: PR #208 opened against `main` for task102 Qwen scale-up remote-root portability.
57. supervisor request: PM assigned task105 to sync latest main, ensure Qwen scale-up local training-plan rendering passes `--qwen-hf-model`, preserve separate tokenizer handling, add focused tests, open a PR, and avoid live runs/main push/self-merge.
58. technical fact: `render_local_data_prep_script()` already rendered `--tokenizer-model` for `plan_m1_agentic_sft_training.py`, but omitted `--qwen-hf-model`; with separate remote model and local tokenizer paths, the nested plan could record tokenizer path as `training_contract.model_ref`.
59. file change: Qwen scale-up local script rendering now passes `--qwen-hf-model` from `manifest["training"]["qwen_hf_model"]` next to `--tokenizer-model`.
60. test evidence: Task105 focused planner pytest shard passed with 22 tests; py_compile, Ruff, structured separate model/tokenizer render probe, and diff checks passed.
61. file change: PR #210 opened against `main` for task105 Qwen scale-up local plan model-ref contract.
62. supervisor request: PM assigned task106 to sync latest main, make Qwen SFT data prep tokenizer env prefer `SUPER3_M1_TOKENIZER_MODEL`, preserve fallback to `SUPER3_M1_QWEN_HF_MODEL`, add focused tests, open a PR, and avoid live runs/main push/self-merge.
63. technical fact: `qwen_agentic_v0.yaml` previously set `tokenizer.model` directly from `SUPER3_M1_QWEN_HF_MODEL`, so direct data prep could not use a separate tokenizer path.
64. file change: Qwen SFT data prep `qwen_agentic_v0.yaml` now sets `tokenizer.model` from `${oc.env:SUPER3_M1_TOKENIZER_MODEL,${oc.env:SUPER3_M1_QWEN_HF_MODEL}}`.
65. test evidence: Task106 focused Qwen/M1 SFT pytest shard passed with 95 tests and 1 skipped; py_compile, Ruff, structured OmegaConf both-env/fallback probe, and diff checks passed.
66. file change: PR #213 opened against `main` for task106 Qwen SFT data-prep tokenizer env contract.

---
