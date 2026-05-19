# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 60 |

刚做完：task020 Session 2 — 促进门 (promotion gate) 逻辑 (PR #74 /
33b51e7, merged 2026-05-19)。新 module `m1_eval_basket/promotion_gate.py`:

- 三档严重度 `PromotionDecision`: promote / hold / rollback
  (rollback > hold > promote)
- Default thresholds 2% (plan §5.7 "1-2%" tight end)，rollback
  tolerance 1e-4
- Default rollback categories: swe_repo_repair + 全部 tool_use_* +
  instruction_following + multi_turn_instruction + safety_* (forward-
  compat M2)
- Weighting：uniform-per-category, uniform-across-categories
- Missing benchmarks 不挂掉 gate 但 surface 给 operator
- `format_gate_report()` markdown 输出

21 个新 pytest case；sandbox 测试基线 371 → 392 passed + 7 skipped。

**M1 eval basket plan §5.7 acceptance 全 sandbox 部分落地**:
- task019 Session 1 ✓ (8-row v0 registry + schema kind + regression_report.py)
- task020 Session 1 ✓ (11-row full extension + combined config)
- task020 Session 2 ✓ (promotion gate logic)
- 接下来只剩 cluster verify (task019 S2-3 + task020 S3) — 都需 cluster
  + 真 SFT checkpoint + 真 Super3 baseline numbers
- task019 Session 4 acceptance (promotion gate) 由 task020 Session 2 提供

下一候选 (sandbox-runnable):
- **task020 Session 4** — per-category gap analysis tooling，layer on
  top of Session 2。Sandbox-runnable，但 plot 真数据需要 Session 3
  cluster 跑完
- task014 / 016 / 017 / 018 各自 Session 2 (converter 单测，sandbox 部分)
- 之前 task 的 Session 2+ — 大都需 cluster
