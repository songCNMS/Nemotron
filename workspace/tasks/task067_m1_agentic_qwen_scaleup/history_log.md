# task067_m1_agentic_qwen_scaleup - history

<!-- METADATA:SESSION=2 -->

## Session 1

- 从 Idle 接手用户请求“继续下一步”，基于 task066 merge 后状态进入正式放大训练入口开发。
- 分支：`intern_nemontron_code_reading/task067_m1_agentic_qwen_scaleup`。
- 新增 `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py`，生成 `run_local_data_prep.sh`、`sync_to_nemtron.sh`、`run_nemtron_train.sh`、`run_eval_basket_dry_run.sh`、manifest 和 report。
- planner 默认只选择 M1 Agentic SFT 支持的 11 个 M0 public data slices，排除 SWE1/SWE2/RLHF 专用 `m0_swe_pivot_tool_call`、`m0_swe2_openhands_trace`、`m0_helpsteer2_pref`。
- 新增 `tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py`，覆盖 dataset allowlist、Qwen TP=2 remote train script、eval basket dry-run 和 executable outputs。
- 修复远端 tmux launch 中 `TRAIN_ITERS` 只在 ssh shell 里定义的问题，生成脚本会 `export TRAIN_ITERS` 供 tmux 新 session 使用。
- 验证：ruff passed；`pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py` → 54 passed, 1 skipped；`m1_basket` eval dry-run passed。
- 生成 planner smoke：`/work-agents/intern_nemontron_code_reading/outputs/task067_plan_smoke`，参数为 train=10 / val=3 per dataset、pack/seq length 512、8 shards、eval config `m1_basket`。

## Session 2

- 复验 PR #93：ruff passed；`pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py` → 54 passed, 1 skipped；`m1_basket` eval dry-run passed。
- 按 playbook 在分支上将 task067 README 标记为 Completed，将 intern status 切回 Idle，并准备合并 PR #93。
