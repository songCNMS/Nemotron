# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，登记 task001 review 中遗留的 3 项次优先级修复。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

接受任务并完成全部 3 项次优先级修复 + 4 个回归测试。

分支 `intern_nemontron_review_cc/task002_m0_secondary_fixes`，PR <https://github.com/songCNMS/Nemotron/pull/5>，状态 CLEAN/MERGEABLE，等审。

涉及文件（与 task001 同一批）：
- `src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py`
- `src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml`
- `tests/recipes/super3/test_m0_data_env.py`
- `tests/recipes/super3/test_m0_health_baseline.py`

修复要点：
1. **#7 Hermes 多轮**：移除 `convert_hermes_conversations` 在第一条 assistant 处的 `break`；新增 `HERMES_ROLE_MAP` 包含 tool / function / function_response / observation；返回字典加 `expected_trajectory` / `expected_final_content` / `expected_turn_count`；`transform_hermes_function_calling` 把这三项落到 `extra_env_info`。`expected_tool_calls` / `expected_assistant_content` 仍是首轮值（向后兼容）。
2. **#8 hermes hf_config**：`data_registry.yaml` 锁定 `func_calling_singleturn`；注释说明该 config 只有 `train` split，故继续走 task001 的 fallback 警告路径。
3. **#15 aggregate 重复执行**：`evaluate_policy` 拆成 `score_rows` + `aggregate_scored_rows`；`summarize_baselines` 缓存 split-级 scored 结果，aggregate 由拼接得到，subprocess fork 数量减半；`evaluate_policy` 改成两函数的薄封装，签名不变。

测试：
- `PYTHONPATH=src pytest tests/recipes/super3/ -v` → **24 passed**（原 20 + 新 4）。
- 新增 case：hermes multi-turn trajectory、hermes hf_config 锁定、monkeypatch counter 验证 aggregate 不重算（3 行 oracle 只 score_record 3 次）、score_rows + aggregate_scored_rows 与 evaluate_policy 行为等价。

待办：PR #5 review / merge。
