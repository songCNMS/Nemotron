# task002_m0_secondary_fixes

<!-- METADATA:STATUS=Open,ASSIGNEE= -->

## 背景

PR #4 已合并主干，落地了 M0 review 中 4 项 correctness 修复。Review 里还有 3 项次优先级问题，独立性较高，单独成 task：

1. **#7 Hermes 多轮丢失**：`convert_hermes_conversations` 在第一条 `assistant` 出现时 `break`，整段 multi-turn tool 轨迹（tool 结果 → 第二条 assistant final answer）被丢弃。Hermes function-calling 大量样本是多轮，目前 M0 把"general tool calling"窄化为"first-turn tool emission"。
2. **#8 hermes `hf_config: null`**：`NousResearch/hermes-function-calling-v1` 是多 config 数据集（`func_calling_singleturn` / `func_calling` / `glaive_func_calling` / `json_mode_singleturn` 等）。当前 `hf_config: null` 会让 `load_dataset` 行为不稳定。需要显式选 config。配合任务 #4 已加的 `hf_val_split` 机制，把 hermes 也接入真正 holdout。
3. **#15 aggregate 重复执行测试**：`summarize_baselines` 对 train / val 各跑一次 `evaluate_policy`，又把它们拼起来再跑一次 aggregate；对 code_execution_python 来说 subprocess fork 数量翻倍。aggregate 应该由 split 结果合并算出来。

## 目标

修复 3 个次优先级问题，保持 JSONL 顶层 schema 与 manifest 字段名前向兼容。

## 验收标准

- [ ] **#7**：Hermes 转换不仅捕获第一条 assistant 的 tool calls / content，还把后续 tool 结果 / assistant final answer 折进 `extra_env_info.expected_trajectory`（list of turns，每个 turn 含 role + tool_calls + content）；同时新增 `extra_env_info.expected_final_content`（最后一条 assistant 的纯文本）。`expected_answer` 仍取第一条 assistant 的 tool calls / content（保持 wiring 兼容）。
- [ ] **#8**：`data_registry.yaml` 的 hermes spec 把 `hf_config` 改为显式 `func_calling_singleturn`；加 `hf_val_split: ...`（用同一 config 内的 `train` 切片或它的 sibling subset；如果 singleturn 只有一个 split，就在 README/manifest 显式标注 fallback 仍是顺序切片）。
- [ ] **#15**：`summarize_baselines` 重构：`evaluate_policy` 拆出"per-row score collection"和"aggregate metrics"两段。split 与 aggregate 共用 score 缓存；code_execution_python 每条记录的 subprocess 只跑一次（aggregate 由 split 计数相加得到）。
- [ ] 新增 / 调整测试覆盖上述 3 点，`PYTHONPATH=src pytest tests/recipes/super3/` 全绿。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml`
- `tests/recipes/super3/test_m0_data_env.py`
- `tests/recipes/super3/test_m0_health_baseline.py`
- 上一轮 PR：https://github.com/songCNMS/Nemotron/pull/4
