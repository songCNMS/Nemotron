# task005_m1_sft_v0_scope_expansion

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## 背景

`docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §8 把 Agentic SFT v0 的覆盖面定义为：

- tool call syntax
- terminal basics
- search pattern
- structured output
- 短 SWE traces
- 负例（malformed tool call、hallucinated tool output）

但当前 `src/nemotron/recipes/super3/milestones/m1_agentic_sft/` 与 M0 注册表只覆盖了其中 ~4 项：

| Plan 项 | 当前实现 | 来源 |
|---|---|---|
| search pattern | ✓ `search_grounded_qa` | hotpotqa/hotpot_qa |
| tool call syntax | ✓ `general_tool_calling` | NousResearch/hermes-function-calling-v1 (singleturn) |
| short SWE traces | ✗ | — |
| terminal basics | ✗ | — |
| structured output | ◐ `structured_outputs_json` | NousResearch/hermes-function-calling-v1 (`json_mode_singleturn`) |
| malformed tool call 负例 | ✗ | — |
| hallucinated tool output 负例 | ✗ | — |
| reasoning（plan 中 RLVR 项，SFT v0 也需要 reasoning 形态范例） | ✓ `math_reasoning_numeric` | openai/gsm8k |
| code | ✓ `code_execution_python` | google-research-datasets/mbpp |

M0 health gate 已稳定，task003 / task004 把 M1 现有 4 个 env 的 correctness / config / planner 收紧。下一步是把 SFT v0 的训练面铺齐到 plan 文档 §8 描述的水平，再进入 M1 RL。

## 目标

补全 Agentic SFT v0 缺失的 4 类 supervision：terminal basics、short SWE traces、structured output、负例（malformed tool call + hallucinated tool output）。每类都要：

1. 选定公开数据源并锁定 `hf_revision`。
2. 在 `data_registry.yaml` 与 `environment_registry.yaml` 中注册（沿用 M0 schema）。
3. 在 `prepare_m0_assets.py` 加 converter，把原始样本规范化到现有 NeMo-Gym JSONL。
4. 在 `prepare_m1_agentic_sft.py` 加 SFT supervision builder，确保 chat template 渲染正确（含 `tool_calls[].id` / `tool_call_id`，避免 task003 修过的回归）。
5. 在 `run_m0_health_baseline.py` 补 verifier 钩子或显式 stub，使 health gate 仍能通过。
6. 在 tests/recipes/super3/ 加回归用例。

## 子任务拆解

### A. Terminal basics

候选公开数据源（按优先级）：

- `princeton-nlp/SWE-Gym-Lite` 中的 bash 子集（如可剥离）。
- `THUDM/agent-flan` / `THUDM/AgentInstruct` 的 OS/Linux 子集，需要确认 license。
- `microsoft/orca-agentinstruct-1M-v1` 的 shell 子集（CC-BY-4.0）。

环境名建议：`terminal_basic_shell`，verifier 走 `command_substring_match` + 单步 exit-code 占位（M0 不接真 sandbox，沿用 oracle smoke 形态）。

### B. Structured output

候选数据源：

- `Vezora/Tested-22k-Python-Alpaca` 的 JSON 子集。
- `Aeala/ShareGPT_Vicuna_unfiltered` 中的 JSON-mode 转换样本（需重新打 license 标）。
- 直接复用 hermes `json_mode_singleturn` config，独立成第二个 hermes 环境 `structured_outputs_json`。

最稳的路径是复用 hermes `json_mode_singleturn` —— 与现有 tool calling 同源、license/revision 已知。converter 与现有 hermes 流类似，但 expected_answer 是 JSON 而不是 tool_calls。

### C. Short SWE traces

候选数据源：

- `princeton-nlp/SWE-Bench_Lite` 的 issue + patch（公开）—— 仅取 issue text + gold patch 做 SFT，不进 sandbox。
- `THUDM/SWE-Fixer` 的 trace 数据，需 license 复核。

环境名建议：`swe_pivot_patch_supervision`。reward verifier 写 stub（`patch_diff_match`），实际 reward 由 M1 SWE-RL stage 接管。

### D. 负例（malformed tool call + hallucinated tool output）

公开数据源稀缺，建议合成：

- 从 Hermes `func_calling_singleturn` 中已经合规的样本派生：
  - malformed tool call: 截断 JSON、缺 close brace、错 key 等。
  - hallucinated tool output: 把 tool 角色 turn 替换为 "看似合理但与 schema 不匹配" 的合成 string。
- 每条负例必须带 `metadata.negative_kind` 与 `metadata.repair_target`（修复后的正确轨迹），供 SFT v1 / RL repair 阶段复用。

`environment_registry.yaml` 中新增 `tool_call_repair_negative`，verifier 走 `negative_recognition`（模型应识别错误并复述修复后的调用）。

### E. SFT 数据扩展

`prepare_m1_agentic_sft.py` 当前的 `ASSISTANT_BUILDERS` 只有 `search / code / reasoning` 三个，tool 走 `trajectory_for_tool_calling`。新环境的 supervision 需要在那一层加 builder：

- `terminal_basic_shell` → assistant = 命令字符串 + 注释（content-only）。
- `structured_outputs_json` → assistant = JSON 字符串（content-only）。
- `swe_pivot_patch_supervision` → assistant = unified diff 文本。
- `tool_call_repair_negative` → assistant = "我注意到调用不合 schema，正确的调用是 …" + 正确 tool_calls。

确保所有新数据共用 `super3_agentic_sft_v0` `used_in` 标签，blend 由 `prepare_m1_agentic_sft.build_blend` 统一收口。

## 验收标准

- [ ] `data_registry.yaml` / `environment_registry.yaml` 新增 4 个环境，schema 与现有一致，每条带 `hf_revision` / `license` / `contamination`。
- [ ] `prepare_m0_assets.py` 4 个 converter，对每个 converter 至少 1 个单元测试覆盖核心字段。
- [ ] `prepare_m1_agentic_sft.py` 对新环境的 supervision 通过 chat template smoke (`agentic_v0.yaml` data prep + 至少 1 个 packed parquet round-trip 单测) —— 避免 task003 修过的 tool_call_id 回归。
- [ ] `run_m0_health_baseline.py` 把新 verifier 注册到 `score_record`，oracle baseline 在 `--skip-code-execution` 之外都能 pass。
- [ ] `tests/recipes/super3/test_m0_*.py` / `test_m1_agentic_sft.py` 全绿；新增至少 8 个 case（每环境 prep + SFT supervision 各 1）。
- [ ] `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §8 中 v0 的 6 项覆盖面，在 `README.md`（M0 + M1）中有对应表格说明。
- [ ] 末尾的 SFT 数据 blend 在 `prepare_m1_agentic_sft` manifest.counts 中按环境分桶展示。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml`
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml`
- `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §8
- 上一轮 review 报告（task003 / task004 已合并）
