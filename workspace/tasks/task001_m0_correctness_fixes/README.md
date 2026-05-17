# task001_m0_correctness_fixes

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

`docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §3 把 M0 设为 "数据与环境前置基线"。`src/nemotron/recipes/super3/milestones/m0_data_env/` 已经落地 4 个环境（`search_grounded_qa`、`code_execution_python`、`general_tool_calling`、`math_reasoning_numeric`）的 prepare + health/baseline 脚本。

Review 发现 4 个 correctness 类问题会让 health gate 失效或产出错误信号：

1. **Hermes 空 expected 假阳性**：`prepare_m0_assets.transform_hermes_function_calling` 在 `expected_tool_calls` 和 `expected_assistant_content` 都为空时仍写出记录；下游 `score_text("", "")` 返回 1.0，oracle baseline 被打成"通过"。
2. **`--skip-code-execution` 必 fail**：`score_record` 在跳过时返回 0.0，`overall_status` 又把 oracle.pass_at_1 != 1.0 视为失败 → 此 flag 永远拉红 health。
3. **空 / 缺失 input-dir 假 pass**：`discover_environment_rows` 返回空 dict 时，`overall_status` 走到默认 `return "pass"`，CI 误用空目录拿到绿灯。
4. **train/val 非真正 holdout**：当前从 `hf_split: train` 顺序切片，val 只是 train 的延续。GSM8K / MBPP 自带 test split 未使用，违背 plan 文档 §6 "每个环境维护 train/dev/shadow-eval split"。

## 目标

修复以上四个 correctness 问题，并补回归测试。不改变 JSONL 顶层 schema。

## 验收标准

- [ ] Hermes：当一条 Hermes 行的 `expected_tool_calls` 与 `expected_assistant_content` 同时为空时，跳过该行并在 `manifest["errors"]` 记录。
- [ ] `score_text` / `score_tool_call` 不再对 `(candidate="", expected="")` 返回 1.0；空 expected 视为数据缺陷，返回 0 并附 diagnostic。
- [ ] `score_record` / `evaluate_policy` 引入 `skipped` 状态，跳过的行不计入 pass@1 也不计入失败；report 中单列展示。
- [ ] `overall_status` 在以下任一情况下返回 `fail`：input_dir 不存在；扫描后没有任何已知环境；所有 oracle 都被 skip。
- [ ] `data_registry.yaml` 为 GSM8K、MBPP 至少补 `hf_val_split` 字段；`prepare_assets` 优先读 val_split，缺失时 fallback 旧行为并 warn 到 manifest。
- [ ] `tests/recipes/super3/test_m0_*.py` 新增 4 个回归用例覆盖上述行为，且 `pytest tests/recipes/super3/test_m0_*.py` 全绿。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml`
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml`
- `tests/recipes/super3/test_m0_data_env.py`
- `tests/recipes/super3/test_m0_health_baseline.py`
- `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §3 / §6
