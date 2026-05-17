# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 intern_nemontron_review_cc 创建任务，按 REVIEW_v0.md 的推荐顺序先收 P0 两条（#2 + N2）。

## Session 1 - 2026-05-17 - intern_nemontron_review_cc

完成 P0 两条修复 + 4 个回归测试。

分支 `intern_nemontron_review_cc/task004_m1_p0_fixes`，PR <https://github.com/songCNMS/Nemotron/pull/11>，CLEAN/MERGEABLE。

修复要点：
1. **P0 #2 GBS×DP guard** — `plan_m1_agentic_sft_training.py` 新增 `ensure_batch_geometry()`，`build_plan()` 入口校验 `gbs % (dp × mbs) == 0`。默认 `--global-batch-size` 4 → 8。
2. **P0 N2 smoke yaml** — `m1_agentic_smoke.yaml` 的 `pretrained_checkpoint` 改回 YAML literal null；train yaml 不动（finetune=true 仍要求 env var）。

测试：`PYTHONPATH=src pytest tests/recipes/super3/ -q` → 49 passed（task003 基线 45 + 新 4）。

REVIEW_v0.md v3：#2 + N2 标 ✓ Fixed by PR #11。
