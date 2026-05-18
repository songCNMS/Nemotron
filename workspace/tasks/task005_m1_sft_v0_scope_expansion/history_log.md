# history_log

<!-- METADATA:SESSION=2 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 review 流程登记任务，覆盖 plan 文档 §8 中 v0 仍未实现的 4 类 supervision。
- 未 assign，等待资源（数据源 license 复核 + 合成负例 prompt）。

## Session 1 - 2026-05-18 - intern_nemontron_code_reading

- 按 `docs/implementation-roadmap.md` 推荐顺序接手 task005。
- 本轮先实现 structured output 最小闭环：复用 Hermes `json_mode_singleturn`，新增 `structured_outputs_json` M0 环境、converter、`json_value_exact_match` verifier、M1 SFT builder、README 和单元测试。
- 合并 PR #18，将 structured output 最小闭环进入 `main`。
- 继续补齐 terminal basics、short SWE traces、repair negatives 三个切片：
  - `terminal_basic_shell` 使用 `aelhalili/bash-commands-dataset`，新增 bash command converter、`command_substring_match` verifier、M1 content-only command builder。
  - `swe_pivot_patch_supervision` 使用 `princeton-nlp/SWE-bench_Lite` issue + gold patch，新增 patch converter、`patch_diff_match` verifier、M1 unified-diff builder。
  - `tool_call_repair_negative` 从 Hermes `func_calling_singleturn` 派生 malformed / hallucinated repair negatives，写出 `negative_kind`、`repair_target`、repair message 和 corrected `tool_calls`。
- 单元测试扩展到 M0 converter、health verifier、M1 supervision builder 三层；本地目标测试为 `83 passed, 2 skipped`。
- 小样本 smoke 已跑通：三个新 slice 各生成 `2 train / 1 val`，M0 health baseline `status=pass`，M1 SFT 输出 `6 train / 3 val_shadow` 且 `errors=0`。
- 代码已提交到 PR #19：`intern_nemontron_code_reading/task005_remaining_agentic_sft_v0_envs`。

## Session 2 - 2026-05-18 - intern_nemontron_code_reading

- 合并 PR #19，将 terminal basics、short SWE traces、repair negatives 三个切片进入 `main`，merge commit 为 `3e376167881fa8c07f1deb1a2d9262d1fcb68bb5`。
- 进入 M1 SFT packed data round-trip 验证入口；当前 CPU venv 缺少完整 data-prep 运行依赖 `cosmos_xenna` 和 `transformers`，因此先新增轻量 `run_m1_sft_roundtrip_smoke.py`。
- round-trip smoke 复用 M1 JSONL、Nano3 chat template、assistant loss mask、packed parquet 写入/读回 schema 检查，避免在完整 Xenna pipeline 前遗漏格式问题。
- 验证中发现并修复 repair-negative 两个问题：
  - malformed artifact 的 raw `<tool_call>` 会触发 data-prep validator，被改为 prompt 中转义标签，`extra_env_info.invalid_artifact` 仍保留原始 artifact。
  - repair-negative 原先连续两个 user turn，会导致 Nano3 增量渲染 mismatch，被改为单个 user turn 合并原始请求与 repair 指令。
- 小样本验证已跑通：三个新 slice 各生成 `2 train / 1 val`，M0 health baseline `status=pass`，M1 SFT 输出 `6 train / 3 val_shadow`，round-trip packed parquet 输出 `1` 个 row、`3978` tokens、`802` assistant loss tokens。
- 本地目标测试：`PYTHONPATH=src pytest -q tests/recipes/super3` 为 `84 passed, 2 skipped`；`git diff --check` 通过；`ruff` 在 `/work-agents/.venv` 中不可用。
- 代码已提交到 PR #21：`intern_nemontron_code_reading/task005_m1_sft_roundtrip_session2`。
