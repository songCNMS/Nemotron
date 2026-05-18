# history_log

<!-- METADATA:SESSION=1 -->

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
