# task067_m1_agentic_qwen_scaleup

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemontron_code_reading -->

## Background

task066 已在 NemTron 上完成 Qwen3 4B M1 Agentic SFT 13-iteration smoke，并修复了 dataset CLI overrides 未进入 dataset config 的问题。下一步需要把同一条链路扩大到更正式的数据规模、训练步数和 M1 eval basket。

## Goals

- 提供可复用的 Qwen M1 Agentic SFT scale-up planner，串起 M0 数据准备、M1 Agentic SFT 转换、Qwen tokenizer packed data prep、training planner、NemTron 启动和 eval basket dry-run。
- 明确默认 agentic SFT 数据切片、Qwen 路径、checkpoint 路径、输出目录和可调参数。
- 用测试覆盖命令生成逻辑，避免后续手写命令漂移。

## Acceptance

- [x] planner 能生成本地数据准备脚本、NemTron 训练脚本、manifest 和 report。
- [x] 生成的命令包含 M1 agentic SFT 支持的 11 个公开数据切片，不误纳 SWE1/SWE2/RLHF 专用数据。
- [x] 生成的训练脚本使用 Qwen3 4B TP=2、planner 产物、正式 eval basket dry-run 入口。
- [x] 相关测试通过。

## Results

- Added `plan_qwen_scaleup_run.py` for Qwen M1 Agentic SFT scale-up planning.
- Generated smoke plan at `/work-agents/intern_nemontron_code_reading/outputs/task067_plan_smoke`.
- Focused validation: ruff passed; `tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` + `tests/recipes/super3/test_m1_agentic_sft.py` → 54 passed, 1 skipped; `m1_basket` eval dry-run passed.
