# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，PR #11 (task004 P0) 合并后按 REVIEW_v0.md 推荐顺序继续 P1。
- 范围只收两条"一行修"P1（#3 GSM8K marker + N1 Qwen 默认路径），#4/#11/#14 留后续 task。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

完成 P1 #3 + N1 修复 + 4 个回归测试。

分支 `intern_nemontron_review_cc/task006_m1_p1_fixes`，PR <https://github.com/songCNMS/Nemotron/pull/12>，CLEAN/MERGEABLE。

修复要点：
1. **#3 GSM8K `####` marker** — `assistant_for_reasoning` 优先用 `expected_answer`；fallback 用 `_strip_gsm8k_marker` 去掉 `####\s*`。
2. **N1 Qwen 默认路径** — `qwen_local_train.py` 删 `DEFAULT_QWEN_MODEL`，改成 `resolve_qwen_hf_model()` 必填 `SUPER3_M1_QWEN_HF_MODEL`；torch/megatron import 推迟到运行时方便单测。

测试：`PYTHONPATH=src pytest tests/recipes/super3/ -q` → 52 passed（task004 基线 49 + 新 3，并把旧的 `test_convert_reasoning_record_uses_reference_solution`-断言的是 buggy 行为-重写为 prefer_expected_answer）。

REVIEW_v0.md v4：#3 / N1 / #16 全部标 ✓ Fixed by PR #12。
