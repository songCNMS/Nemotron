# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### Hermes function-calling 的 config 选择

`NousResearch/hermes-function-calling-v1` 在 HF hub 上有多个 config：
- `func_calling_singleturn` — 单轮工具调用（M0 当前默认）。
- `func_calling` — 多轮工具调用 + 最终答案。
- `glaive_func_calling` — Glaive 来源、风格略不同。
- `json_mode_singleturn` / `json_mode_agentic` — JSON 结构化输出。

每个 config 只有 `train` split，没有官方 holdout，所以 `prepare_m0_assets` 对 hermes 一直走"sequential val 切片 + manifest.warnings"的 fallback。

未来 M1 / M2 启用 agent loop（`general_tool_calling` 环境 `max_turns > 2`）后再切到 `func_calling` 多轮 config；目前的 #7 fix 已经把多轮轨迹收集进 `extra_env_info.expected_trajectory`，切 config 后只需把环境 `max_turns` 调大并让 verifier 消费 trajectory。

### M0 baseline 的 subprocess 成本

`code_execution_python` env 跑一次 health baseline 时：
- per-row × per-policy × per-candidate 调一次 subprocess（`run_python_unit_tests`）。
- 三个 policy（oracle / empty / oracle_then_empty）candidates 数量分别是 1 / 1 / 2。

task002 之后 aggregate 不再重跑 verifier，所以 N 行总 subprocess 次数 = N × (1+1+2) = 4N。
（task001 当时是 8N，task002 减半到 4N。）
