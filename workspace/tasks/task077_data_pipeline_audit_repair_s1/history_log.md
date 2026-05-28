# task077_data_pipeline_audit_repair_s1 - History log

<!-- METADATA:SESSION=16 -->

---

## Session 1 - 2026-05-28 - Qwen data-prep guard and M1 audit

**Executor**: intern_nem_dev_1

- Synced local `main` to `ffcf0ae247400f1da8f4b0a20e32e4d2c6393795` before work; no fast-forward blocker.
- Created branch `intern_nem_dev_1/task077_data_pipeline_audit_repair_s1`.
- Added a Qwen-safe SFT data-prep config and shared Qwen packing-contract validator.
- Updated the Qwen scale-up planner to use the Qwen config and reject Super3/Nemotron drift statically.
- Added M1 manifest/report audit fields for source metadata, split routing, normalized prompt duplication, and output SHA256 fingerprints.
- Updated synthetic V7/V8 tests to explicitly acknowledge the decontamination skip used only by local fixtures.
- Opened PR #186 against `main`: https://github.com/songCNMS/Nemotron/pull/186

---

## Session 8 - 2026-05-28 - PR status recorded

**Executor**: intern_nem_dev_1

- Confirmed PR #186 is open against `main` for branch `intern_nem_dev_1/task077_data_pipeline_audit_repair_s1`.
- Base SHA: `ffcf0ae247400f1da8f4b0a20e32e4d2c6393795`.
- Head SHA after PR status commit: `e6bed5b5fb6f88db774f4525f1cdf33f535d8d5a`.
- Recorded validation evidence in intern report and task knowledge.
- PM peer notification was attempted and returned `{"status": "undeliverable", "reason": "busy"}`.

---

## Session 9 - 2026-05-28 - Task080 bridge audit recovery

**Executor**: intern_nem_dev_1

- Read `/work-agents/intern_nem_dev_1/instruction.md` section `2026-05-28 16:12 UTC - PM recovery after 413 for task080`.
- Continued branch `intern_nem_dev_1/task080_m1_bridge_data_quality_s1` from base `95ddee2f55df4c6d76134f7ea22d5ed5092b6732`.
- Added shared M1 bridge data-quality audit helpers and SHA-256 output-fingerprint helpers in `_bridge_base.py`.
- Wired `data_quality` and `output_fingerprints` manifest/report blocks into RLVR, SWE1, SWE2, and RLHF bridge writers.
- Added focused bridge assertions for all four bridge families and opened PR #189: https://github.com/songCNMS/Nemotron/pull/189
- Validation: `PYTHONPATH=src python -m pytest tests/recipes/super3/test_m1_rlvr_data_bridge.py tests/recipes/super3/test_m1_swe1_data_bridge.py tests/recipes/super3/test_m1_swe2_data_bridge.py tests/recipes/super3/test_m1_rlhf_data_bridge.py` passed with 65 tests; `git diff --check` passed. `python -m ruff check ...` was attempted but Ruff is not installed.

---

## Session 10 - 2026-05-28 - Task080 lineage docs follow-up

**Executor**: intern_nem_dev_1

- Read `/work-agents/intern_nem_dev_1/instruction.md` section `2026-05-28 16:26 UTC - PM follow-up for PR #189 task080 lineage docs`.
- Added docs/lineage-only task080 files: `README.md`, `history_log.md`, and `task_knowledge.md`.
- Recorded PR #189 scope, URL, base/head, changed files, validation evidence, residual risk, and no main/master push or merge.
- Product code unchanged in this follow-up.

---

## Session 11 - 2026-05-28 - Task080 ruff gate fix

**Executor**: intern_nem_dev_1

- Read `/work-agents/intern_nem_dev_1/instruction.md` section `2026-05-28 16:25 UTC - PM follow-up for PR #189 task080 ruff gate`.
- Applied a narrow import/lint-only fix for PR #189 after PM reported Ruff `I001` and `F401`.
- Ran `/work-agents/.venv/bin/ruff check --fix ...`, inspected the diff, and preserved `KNOWN_STATUSES` as an explicit re-export while removing unused `read_jsonl` imports.
- Validation passed: exact PM Ruff command, `PYTHONPATH=src python -m pytest -q` focused bridge shard with 65 tests, `python -m py_compile` for touched bridge modules/tests, and `git diff --check`.
- No direct push to `main` or `master`; no self-merge.

---

## Session 12 - 2026-05-28 - Task086 Qwen SFT data-prep default contract

**Executor**: intern_nem_dev_1

- Received PM correction to ignore misdelivered task085/stage3 eval work; task085 belongs to intern_nem_dev_3.
- Read task086 instructions from `/work-agents/intern_nem_dev_1/instruction.md`.
- Synced local `main` to `d2f37f7e647bce186922f41da9476fa6e734576c` and created branch `intern_nem_dev_1/task086_qwen_sft_data_prep_default_contract_s1`.
- Changed the Super3 SFT data-prep runspec/direct-script runnable default to `qwen_agentic_v0` so the default path cannot silently pack Super3/Nemotron rows for the current Qwen target.
- Preserved legacy Super3/Nemotron data-prep configs for explicit config selection and updated docs/tests to make the default contract clear.
- Validation passed locally: focused Qwen contract test, required Qwen/SFT pytest shard, py_compile, Ruff on touched Python files/tests, and `git diff --check`.
- Opened PR #192: https://github.com/songCNMS/Nemotron/pull/192

---

## Session 13 - 2026-05-28 - Task087 stage2 RL bridge data-prep defaults

**Executor**: intern_nem_dev_1

- Read task087 instructions from `/work-agents/intern_nem_dev_1/instruction.md`.
- Confirmed local `main`, `origin/main`, and task branch base at `3d313bcb7dbd6044b1202774741697f37d99a485`.
- Created branch `intern_nem_dev_1/task087_stage2_rl_data_prep_bridge_defaults_s1`.
- Added SWE1/SWE2/RLHF bridge `combined.jsonl` outputs as train rows followed by val rows, with manifest/report/lineage/output-fingerprint coverage.
- Rewired SWE1/SWE2/RLHF stage2 RL data-prep defaults from developer-local `/lustre` release files to templated M1 bridge combined outputs.
- Validation passed locally: required bridge/default pytest shard, py_compile for touched Python files/tests, Ruff on touched Python files/tests, `git diff --check`, and `git diff --cached --check`.
- Opened PR #194: https://github.com/songCNMS/Nemotron/pull/194

---

## Session 14 - 2026-05-28 - Task090 Nano3 stage0 pretrain output portability

**Executor**: intern_nem_dev_1

- Read task090 instructions from `/work-agents/intern_nem_dev_1/instruction.md`.
- Fast-forwarded local `main` to `c26dedfcbff336e3f827f59f39230d713d260e29` and created branch `intern_nem_dev_1/task090_nano3_stage0_pretrain_data_prep_output_portability_s1`.
- Replaced Nano3 stage0 pretrain `default.yaml` `output_dir` named-user `/lustre` default with `${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain`, matching the recipe-local dataclass default contract.
- Preserved existing `tiny.yaml` behavior and added focused static tests for Nano3 stage0 pretrain data-prep required fields and portable output dirs.
- Validation passed locally: focused Nano3 config pytest shard, py_compile for touched test, Ruff for touched test, static output_dir scan, `git diff --check`, and `git diff --cached --check`.
- Opened PR #197: https://github.com/songCNMS/Nemotron/pull/197

---

## Session 15 - 2026-05-28 - Task092 Nano3 stage2 RL Qwen contract

**Executor**: intern_nem_dev_1

- Read task092 instructions from `/work-agents/intern_nem_dev_1/instruction.md` and ignored unrelated generic prompt text.
- Fast-forwarded local `main` to `914dc3db746702744651a97ea8680087e582a6fb` and created branch `intern_nem_dev_1/task092_nano3_stage2_rl_qwen_contract_s1`.
- Updated Nano3 stage2 RL `default.yaml` and `tiny.yaml` to pin tokenizer and vLLM serving `chat_template_kwargs` with `enable_thinking=false` and `truncate_history_thinking=false`.
- Added `<|im_end|>` generation stop string and switched HTTP serving parser contract from `deepseek_r1` to `nano_v3` with `nemo_rl/utils/nano_v3_reasoning_parser.py`.
- Added focused static tests proving default/tiny satisfy the Nano3 Qwen RL contract and do not drift from each other.
- Validation passed locally: focused Nano3 Qwen RL pytest shard, py_compile for touched test, Ruff for touched test, structured YAML probe, `git diff --check`, and `git diff --cached --check`.
- Suggested existing integration shard was attempted and is blocked by unrelated pre-existing drift in `tests/recipes/nano3/stage2_rl/test_data_prep_train_integration.py`.
- Opened PR #199: https://github.com/songCNMS/Nemotron/pull/199

---

## Session 16 - 2026-05-28 - Task092 Nano3 tiny validation split follow-up

**Executor**: intern_nem_dev_1

- Read updated task092 instruction from `/work-agents/intern_nem_dev_1/instruction.md`.
- Fixed Nano3 stage2 RL `tiny.yaml` so `data.validation_jsonl_fpath` uses `${art:data,val}` instead of reusing `${art:data,train}`.
- Extended the focused task092 static test to prove tiny train and validation artifact split keys are `train` and `val` and differ.
- Validation passed locally: focused Nano3 Qwen RL contract pytest shard, py_compile for touched test, Ruff for touched test, structured YAML probe including tiny split keys, `git diff --check`, and `git diff --cached --check`.
- Pushed the follow-up to existing PR #199: https://github.com/songCNMS/Nemotron/pull/199

---

## Session 17 - 2026-05-28 - Task095 Super3 GenRM reasoning parser contract

**Executor**: intern_nem_dev_1

- Read task095 instructions from `/work-agents/intern_nem_dev_1/instruction.md`.
- Confirmed branch `intern_nem_dev_1/task095_super3_genrm_reasoning_parser_contract_s1` was based on `90e64c745e6ed905559aacf11125b4d5d3d1f255`.
- Updated Super3 stage1_rlvr and stage3_rlhf GenRM vLLM `server_args` from stale `deepseek_r1` to the Nano3 `nano_v3` reasoning parser plus `nemo_rl/utils/nano_v3_reasoning_parser.py`.
- Added a focused static test walking stage1_rlvr/stage3_rlhf Nemo Gym vLLM model definitions and asserting every `uses_reasoning_parser: true` server matches the rollout parser/plugin contract.
- Validation passed locally: required Super3 parser/stop-string pytest shard, py_compile for touched test, Ruff for touched test, `git diff --check`, and `git diff --cached --check`.
- Opened PR #202: https://github.com/songCNMS/Nemotron/pull/202

---

## Session 17 - 2026-05-28 - Task098 Qwen SFT local train packed-dir contract

**Executor**: intern_nem_dev_1

- Read task098 instructions from `/work-agents/intern_nem_dev_1/instruction.md`.
- Fast-forwarded local `main` to `780626169586fe5be34993deaa49598b7af11a44` and created branch `intern_nem_dev_1/task098_qwen_sft_local_train_packed_dir_contract_s1`.
- Added a shared Qwen local packed-dir default helper that rewrites only the inherited legacy `../output/super3/stage1_sft_agentic_v0/splits` fallback to `../output/super3/stage1_sft_agentic_v0_qwen/splits`.
- Wired both Qwen 4B and Qwen3 30B-A3B local train entrypoints through the helper before packed-data metadata validation.
- Added focused tests proving the 4B and 30B entrypoints rewrite the inherited fallback and preserve explicit config/env packed-dir overrides.
- Validation passed locally: requested M1 Agentic SFT/Qwen scale-up pytest shard, py_compile, Ruff, static OmegaConf packed-dir probe, `git diff --check`, and `git diff --cached --check`.
- Opened PR #205: https://github.com/songCNMS/Nemotron/pull/205

---
