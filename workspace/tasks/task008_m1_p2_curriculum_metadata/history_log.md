# history_log

<!-- METADATA:SESSION=4 -->

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

## Session 2 - 2026-05-17 - intern_nemontron_review_cc

PR #14 已 squash-merge 为 `6d45fe0`；远程 task008 分支删除。task008 结题。

剩余 P3 长尾 + N3 由 task009 承接：#12 used_in lineage / #13 system prompt 文档 / #17 train_iters 注释 / #18 smoke_runtime silent warning / #19 tiny_model silent fallback / #20 user `<tool_call>` 清洗 / #24 cleanup_stale README / N3 hotpotqa trust_remote_code 文档。

## Session 3 - 2026-05-17 - intern_nemontron_review_cc

task008 已结题，本会话无 task008 新动作；主线由 task009 推进（PR #15）。

## Session 4 - 2026-05-17 - intern_nemontron_review_cc

task008 仍无新代码改动。继续追踪父任务链：task009 (PR #15) 已 CLEAN/MERGEABLE，把 P3 长尾 8 条 + N3 全部 ✓ Fixed，REVIEW_v0.md 从 task008 完成时的 9 fixed 推进到 17 fixed。task008 的 `m1_use` per-env / `difficulty_bucket` metadata 与 task009 的 `m0_use_stage` 一起构成 SFT record metadata 的完整 lineage + curriculum 信号面，下游 v1+ curriculum sampler 可直接消费。
