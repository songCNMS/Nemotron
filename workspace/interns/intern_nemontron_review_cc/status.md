# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task020_m1_eval_full_basket -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task020_m1_eval_full_basket |
| PR | pending push |
| Session | 61 |

正在做：task020 Session 4 — per-category gap analysis tooling。跟
Session 2 promotion_gate 互补：gate 给 binary 决策，gap_analysis 给
prescriptive ranking 告诉 operator "下一轮训练 focus 哪里"。新 module
`m1_eval_basket/gap_analysis.py`:

- `BenchmarkGap` / `CategoryGap` frozen dataclass
- `analyze_gaps(current, super3, registry_rows)` — worst-first ranking,
  per-benchmark drill-down 排序 worst-first within category
- `count_categories_below_threshold(gaps, *, threshold)` summary helper
- `format_gap_analysis(gaps, *, threshold)` markdown:
  - Ranked category table (status: behind / on par / ahead / no data)
  - Drill-down section ONLY for below-threshold categories (clean run =
    clean report)
- Missing benchmarks: gap=None when 一侧 missing；category mean 排除
  missing (partial coverage 不被零拖下)
- Default threshold 0.02 matches Session 2 promotion_gate so "behind"
  跟 "in regression" 对齐

17 个新 pytest case；sandbox 测试基线 392 → 409 passed + 7 skipped。

task020 整 task：Sessions 1+2+4 ✓，Session 3 (cluster verify) 仍待 —
需 cluster + 真 SFT checkpoint + 真 Super3 baseline。

**M1 eval basket 全 sandbox 部分 100% 落地** (analysis layer 三件套):
- `regression_report.py` (vs prior checkpoint) — task019 Session 1
- `promotion_gate.py` (vs Super3, binary 决策) — task020 Session 2
- `gap_analysis.py` (vs Super3, prescriptive ranking) — task020 Session 4
