# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，PR #11/#12/#13 合并后按 REVIEW_v0.md 推荐顺序继续 P2。
- 范围：#7 difficulty curriculum metadata + #10 m1_use per-env 切片。其余 P2 (#5/#6) 由 task005 推进。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

完成 P2 两条修复 + 6 个回归测试。

分支 `intern_nemontron_review_cc/task008_m1_p2_curriculum_metadata`，PR <https://github.com/songCNMS/Nemotron/pull/14>，CLEAN/MERGEABLE。

修复要点：
1. **#10 m1_use per-env** — 新增 `M1_USE_BY_ENV`，per-env 切片；`m1_metadata.m1_use` 现在按 record env 取对应 list。
2. **#7 difficulty_bucket** — 新增 `load_difficulty_signal()` 读 M0 `health_baseline_report.json`；`prepare_m1_agentic_sft.py` 加 `--m0-health-baseline` 入口（默认 fallback 自动找）；每条 record 写 `metadata.difficulty_bucket ∈ {trivial, hard, unknown}`；`manifest.difficulty_buckets` 汇总。失败列表截断保护：`failure_count > len(failures)` 时未列 row 留 `"unknown"`，不误判 trivial。

测试：`PYTHONPATH=src pytest tests/recipes/super3/ -q` → 62 passed + 1 skipped（task007 基线 56 + 新 6）。

REVIEW_v0.md v6：#7 / #10 ✓ Fixed by PR #14。整体进度 9 fixed / 1 partial / 9 open / 2 tracked。
