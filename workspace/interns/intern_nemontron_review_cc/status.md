# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task020_m1_eval_full_basket -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task020_m1_eval_full_basket |
| PR | pending push |
| Session | 59 |

正在做：task020 Session 2 — 促进门 (promotion gate) 逻辑。Plan §5.7 /
roadmap §1.7 task020 显式提的：weighted-mean Super3 parity +
no-category-regression > 1-2% + rollback rule on safety / SWE / tool /
IF。新 module `m1_eval_basket/promotion_gate.py`:

- 三档严重度 `PromotionDecision`: promote / hold / rollback
  (rollback > hold > promote)
- Default thresholds 2% (plan "1-2%" tight end), rollback tolerance 1e-4
- Default rollback categories: swe_repo_repair + 全部 tool_use_* +
  instruction_following + multi_turn_instruction + safety_* (forward-
  compat M2)
- Weighting：uniform-per-category, uniform-across-categories (防
  benchmark count gaming)
- Missing benchmarks 不挂掉 gate 但记录在 reasons + missing 列表
- `format_gate_report()` markdown 输出

21 个新 pytest case；sandbox 测试基线 371 → 392 passed + 7 skipped。

task020 整 task 仍 InProgress：Sessions 3-4 待开。Session 3 (cluster
verify) 需 cluster + 真 SFT checkpoint + 真 Super3 baseline，Session
4 (per-category gap analysis) sandbox-runnable 但需要 Session 3 真数
据来调试有意义。

task019 Session 4 acceptance (promotion gate logic) 由 task020 Session
2 提供 — 数据层 (task019 v0 + task020 full) + gate logic (task020
Session 2) 一起完成 plan §5.7 acceptance。
