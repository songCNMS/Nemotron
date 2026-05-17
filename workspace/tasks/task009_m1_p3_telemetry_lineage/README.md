# task009_m1_p3_telemetry_lineage

<!-- METADATA:STATUS=Open,ASSIGNEE= -->

## 背景

PR #11/#12/#13/#14 把 P0 + P1 + P2 #7/#10 全部清完。REVIEW_v0.md 还剩 P3 长尾 8 条 + N3 (hotpotqa README/SECURITY)。本任务挑"telemetry + lineage + docs"小改：

- **#12** M0 `used_in` lineage 被 M1 完全覆盖，无法回溯 M0 阶段标签
- **#13** tool-calling `prompt_messages` 单向重写 system prompt，README 没有说明
- **#17** `train_iters: 1700` 默认值对 M0 smoke 数据严重过大；用户不跑 planner 就吃到这个值
- **#18** `smoke_runtime.patch_dataset_helper_compile_if_prebuilt` import 失败时 silent no-op
- **#19** `tiny_model.py` 在缺 `Nemotron3SuperProvider` 时静默降级到 Nano provider
- **#20** `prompt_messages` 只洗 system，user content 里的 demo `<tool_call>` / `<tools>` XML 不洗
- **#24** M0 `cleanup_stale_split_files` 让 `--overwrite` 删 stale env 目录，README 没说
- **N3** hotpotqa `trust_remote_code: true` 让 HF loader 跑任意 Python，M0 README/SECURITY 没标

留作后续 task 的：#8 (Super3 chat template) / #9 (两阶段 SFT loss) / #15 (chat template render 测试) / #21 (compute_train_iters parquet path) / #22 (端到端 prepare→data prep→planner 测试)。这些都需要新资源（chat template 文件 / pyarrow fixture / 完整 data-prep 栈），独立成大任务。

## 目标

把上述 8 条小改打成一个 PR，不引入功能性 schema change。

## 验收

- [ ] **#12**：`m1_metadata` 在新字段 `m0_use_stage` 写 M0 record 的 `used_in` list。
- [ ] **#13**：M1 README "Supervision Mapping" 表加一段注释说明 tool-calling 的 system prompt 是被 `TOOL_CALLING_SYSTEM_PROMPT` 单向重写的，其他 env 保留 M0 原 system。
- [ ] **#17**：`m1_agentic_train.yaml` 的 `train_iters: 1700` 上方加注释说明默认值是 placeholder，正确做法是先跑 planner 让它根据 packed_train_rows 算出 iter 数。
- [ ] **#18**：`smoke_runtime.patch_dataset_helper_compile_if_prebuilt` 在 except 分支加 `logger.warning(...)` 说明 patch 未生效及原因。
- [ ] **#19**：`tiny_model.py` 的 ImportError 分支加 `logger.warning(...)` 说明退到了 Nano provider。
- [ ] **#20**：`prompt_messages` 对 tool-calling user content 也跑 `strip_tool_call_blocks`（复用 M0 prepare_m0_assets 的 helper 或 inline 一个），并加单测断言 demo XML 不进 user content。
- [ ] **#24**：M0 README 在 `--overwrite` 段落加一行说明同时删除 stale env 子目录。
- [ ] **N3**：M0 README "Public Sources" 表标 hotpotqa 的 `trust_remote_code: true`，并加一行解释 `hf_revision` 是唯一保护。
- [ ] REVIEW_v0.md v7 标 8 条 ✓ Fixed；`PYTHONPATH=src pytest tests/recipes/super3/` 全绿。
