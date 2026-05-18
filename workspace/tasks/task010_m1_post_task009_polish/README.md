# task010_m1_post_task009_polish

<!-- METADATA:STATUS=Done,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

task001 → task009 已经把 REVIEW_v0.md 的 22/24 项落地修复（剩下 #8 chat template、#9 two-stage SFT loss 是设计向，REVIEW 里标 Still open）。Re-review 主干后没有发现新 P0/P1 bug，但定位到 5 个 post-task009 的小问题：

- **D1**：M1 README "Supervision Mapping" 表还是 v1 文案（"assistant short answer"），PR #13 早就把 search supervision 换成 grounded template；reasoning 行没提 GSM8K `####` 截断；tool 行没说 `tool_call_id` propagation。
- **D2**：M1 README 没记录 task008 加的 `--m0-health-baseline` flag 与 `metadata.difficulty_bucket` 字段。
- **D3**：`prepare_m1_agentic_sft.load_difficulty_signal` 对 OSError / `JSONDecodeError` / shape 错误一律 `return {}`，operator 只看到所有行变 `unknown`，没法定位是文件缺失、损坏还是 schema 不对。
- **D4**：`prepare_m1_agentic_sft._difficulty_for` 含一段死代码 (`"val_shadow"` 翻译) ——`convert_split` 永远传 `"train"` / `"val"`，这条分支永不触发。
- **D5**：task008 把 `difficulty_buckets` 落进 `manifest.json` 但 `report.md` 没渲染，operator 必须自己 grep JSON 才能看到 SFT 数据按 hardness 的分布。
- **T21**：REVIEW finding #21（"`compute_train_iters` derived-rows path uncovered"）也顺手补上：现存 test 写 fake parquet bytes，`maybe_count_parquet_rows` 返回 None，从未触发 `train_rows × epochs / global_batch_size` 这条分支。

## 目标

- D1 / D2：把 README 写对，包含新 flag 与新 metadata 字段。
- D3：`load_difficulty_signal` 在每条失败路径 emit `logger.warning`，命名 underlying exception。
- D4：去掉 dead `val_shadow` 分支，注释说明 split tag rewriting 发生在 manifest summary 一层。
- D5：`write_report` 渲染 `difficulty_buckets` + `m0_health_baseline` 字段。
- T21：补 monkeypatch-driven test 覆盖 `build_plan → summarize_split → compute_train_iters` 整条链路，不依赖 pyarrow 也能跑。
- 全部回归通过 `PYTHONPATH=src pytest tests/recipes/super3/`。

## 验收

- [x] M1 README 表更新；新增 "Difficulty signal" 子段；`--m0-health-baseline` flag 与 `metadata.difficulty_bucket` 都有文字说明。
- [x] `load_difficulty_signal` 3 条 warning 路径（missing file / parse error / shape error）+ 对应回归测试。
- [x] `_difficulty_for` 删除死分支，行为不变。
- [x] `write_report` 渲染 difficulty 表 + health baseline 字段。
- [x] 新增 `test_build_plan_derives_train_iters_from_packed_rows` 覆盖 REVIEW #21。
- [x] 把 N2 / N1 系列旧测试加 `pytest.importorskip("omegaconf")` 让 test env 缺 omegaconf 时 cleanly skip（与 cosmos_xenna / megatron.bridge gate 同 pattern）。
- [x] `PYTHONPATH=src pytest tests/recipes/super3/ -q` → **67 passed, 5 skipped, 0 failed**（v7 基线 66 + 1 new = 67；skips：原 2 个 cosmos_xenna / megatron.bridge + 新 3 个 omegaconf）。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/README.md`
- `tests/recipes/super3/test_m1_agentic_sft.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md` (REVIEW #21 闭环)
- task009 PR #15 (`4cb1228`) 之后的 main
