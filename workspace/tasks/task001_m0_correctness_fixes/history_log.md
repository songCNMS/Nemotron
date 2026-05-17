# history_log

<!-- METADATA:SESSION=2 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，登记 4 个 correctness 修复点。
- 任务尚未 assign，等待接受流程。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

接受任务并完成全部 4 项修复 + 回归测试。

提交分支 `intern_nemontron_review_cc/task001_m0_correctness_fixes`，PR <https://github.com/songCNMS/Nemotron/pull/4>。

涉及文件：
- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml`
- `tests/recipes/super3/test_m0_data_env.py`
- `tests/recipes/super3/test_m0_health_baseline.py`

修复要点：
1. `transform_hermes_function_calling` 在 `expected_tool_calls` 与 `expected_assistant_content` 同时为空时 `raise ValueError`；`score_text` / `score_tool_call` 对空 expected 不再判为通过（fix #1）。
2. `score_record` 在 `--skip-code-execution` 时返回 `(None, {"skipped":...})`；`evaluate_policy` 把 None 计入 `skipped_rows`；`overall_status` 在 oracle.scored_rows==0 时 fail（fix #2）。
3. `build_report` 缺失 input_dir 抛 FileNotFoundError；`overall_status` 在 health.environments 为空时 fail（fix #3）。
4. `data_registry.yaml` 给 GSM8K / MBPP / HotpotQA 增加 `hf_val_split`；`prepare_assets` 双流取行；hermes 无 val_split 时 fallback 并 warn 到 `manifest.warnings`；manifest.datasets 增 `val_holdout` bool（fix #4）。

测试：
- `PYTHONPATH=src pytest tests/recipes/super3/ -v` → 20 passed (原 13 + 新 7)。
- 新增 case：hermes 空 expected 拒绝、score_text 空 expected → 0、score_tool_call 空 list 空 content → 0、score_record skipped、evaluate_policy skipped_rows、overall_status 无环境 fail、overall_status oracle 全 skip fail、build_report missing input_dir。

## Session 2 - 2026-05-17 - intern_nemontron_review_cc

PR #4 已 squash-merge 进 main（commit `47cb0ee`），远程分支删除。

后续从 review 中遗留的 3 项次优先级问题（#7 Hermes 多轮、#8 hermes hf_config、#15 aggregate 重复执行）独立成 task002_m0_secondary_fixes，PR <https://github.com/songCNMS/Nemotron/pull/5>，已 squash-merge 进 main（commit `a3a6bdc`）。

task001 结题：M0 全部 7 项 review findings（4 项 correctness + 3 项 secondary）在 main 上都已修复并带回归测试。`PYTHONPATH=src pytest tests/recipes/super3/` 当前 24 passed。
