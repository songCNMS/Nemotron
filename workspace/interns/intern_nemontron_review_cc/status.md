# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 62 |

刚做完：task020 Session 4 — per-category gap analysis tooling (PR #76 /
44c5ec8, merged 2026-05-19)。新 module `m1_eval_basket/gap_analysis.py`:

- `BenchmarkGap` / `CategoryGap` frozen dataclass
- `analyze_gaps(current, super3, registry_rows)` — worst-first ranking,
  per-benchmark drill-down 排序 worst-first within category
- `count_categories_below_threshold(gaps, *, threshold)` summary helper
- `format_gap_analysis()` markdown — ranked table + drill-down ONLY
  for below-threshold categories (clean runs get clean reports)
- Default threshold 0.02 matches Session 2 promotion_gate

17 个新 pytest case；sandbox 测试基线 392 → 409 passed + 7 skipped。

**M1 eval basket 全 sandbox 部分 100% 落地** (analysis trio):
- `regression_report.py` (vs prior checkpoint) — task019 Session 1
- `promotion_gate.py` (vs Super3, binary 决策) — task020 Session 2
- `gap_analysis.py` (vs Super3, prescriptive ranking) — task020 Session 4

task020 整 task：Sessions 1+2+4 ✓ (all sandbox)；Session 3 (cluster
verify — `nemotron super3 eval -c m1_full_basket` 真跑 + W&B publish
+ 真 Super3 baseline) 仍待，需 cluster + 真 SFT checkpoint。

下一候选 (sandbox-runnable):
- task014 / 016 / 017 / 018 各自 Session 2 (converter 单测，sandbox 部分)
- 之前 task 的 Session 2+ — 大都需 cluster
- M1 eval basket 部分都做完了；下一个 productive 方向是 converter
  layer (task014-018 Session 2)
