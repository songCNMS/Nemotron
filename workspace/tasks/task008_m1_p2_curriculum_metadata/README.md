# task008_m1_p2_curriculum_metadata

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

PR #11 / #12 / #13 (task004 / task006 / task007) 合主干后，REVIEW_v0.md 的 P0 + P1 全部 ✓ Fixed。剩余 P2 共 4 条，其中 #5 (SWE/terminal/structured) 与 #6 (negative 例) 由 `intern_nemontron_code_reading` 在 task005 推进；本任务收剩余两条：

- **#7 difficulty curriculum / pass-rate filtering**：plan §6 "先用当前 SFT 模型过滤掉稳定做对的样本，再按 pass rate、judge confidence、rollout length 排序"。当前 `prepare_m1_agentic_sft.py` 全量纳入 M0 train rows、blend 单条 weight: 1.0，忽略 M0 已经写出的 `health_baseline_report.json` 的 oracle pass/fail 信号。
- **#10 `metadata.m1_use` 名实不符**：硬编码 4 项字符串对所有 record 一刀切，且其中 "search grounded answer format" 在 task007 #11 修复前是不对的——尽管现在 search 已模板化、字符串本身已合理，但 per-row 写一份 4 项 list 仍不准确，应按 env 切片到 plan §8 的 5 个目标能力之一。

## 目标

为 SFT v0 数据流写入 difficulty / curriculum 元数据信号 + 让 `m1_use` 按 env 切片。不改变 blend / 训练入口，留给 v1+ 的 curriculum sampler 消费。

## 验收

- [ ] **#7**：`prepare_m1_agentic_sft.py` 增加一个 `--m0-health-baseline` 可选参数（默认 `<m0_input_dir>/health_baseline/health_baseline_report.json`），加载后把每条 M0 记录对应的 oracle pass/fail（必要时取 `aggregate.oracle.failures` row_index 列表）映射到 SFT record 的 `metadata.difficulty_bucket`：
  - `"trivial"` — oracle pass (M0 model 已稳定做对的 row，按 plan §6 应当 down-weight 或排除)
  - `"hard"` — oracle fail (oracle 都做不对，可能数据脏，需要人工 review)
  - `"unknown"` — baseline report 不存在或无该 row 的信号
  以及一个汇总 `manifest["difficulty_buckets"] = {"trivial": N, "hard": M, "unknown": K}`。
- [ ] **#10**：把 `m1_metadata.m1_use` 改成 per-environment 映射：
  - `search_grounded_qa` → `["search pattern"]`（plan §8）
  - `code_execution_python` → `["code solution format", "structured output"]`
  - `general_tool_calling` → `["tool call syntax"]`
  - `math_reasoning_numeric` → `["reasoning answer format"]`
- [ ] 新增 pytest case 覆盖：
  - difficulty_bucket 在 health_baseline_report 存在时落 `"trivial"` / `"hard"`，缺失时落 `"unknown"`
  - manifest 汇总计数正确
  - m1_use per env 切片对四种 env 输出对应的 list
- [ ] REVIEW_v0.md v6 标 #7 / #10 ✓ Fixed by task008 PR；`PYTHONPATH=src pytest tests/recipes/super3/` 全绿。
