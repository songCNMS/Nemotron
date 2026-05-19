# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 56 |

刚做完：task019 Session 1 — M1 eval basket scaffold (PR #70 / b744333,
merged 2026-05-19)。新模块 `m1_eval_basket/` 含 8-benchmark
`m1_eval_basket_registry.yaml` (per plan §5.7 v0) + `regression_report.py`
(load_eval_results / diff_eval_runs 5-status / format_regression_report) +
`stage3_eval/config/m1_basket.yaml` NeMo Evaluator config。新
`eval_basket_registry` schema kind 注册进 `data_registries/schema.py` +
`unified_index.yaml`，**task030 Session 3 auto-unblock & complete**
(之前 6 session closeout 一直挂着的 block 解了 — task030 整 task
Sessions 1+2+3+4+5+6+7 全部落地)。22 个新 pytest case；sandbox
测试基线 335 → 357 passed + 7 skipped。

task019 整 task 仍 InProgress：Sessions 2-4 (cluster verify + W&B publish +
per-benchmark adapter + promotion gate logic) 待开 — 大都需 cluster /
真 SFT checkpoint。

**里程碑**: task030 整 task 这条线全部 Sessions (1+2+3+4+5+6+7) 落地。
下一个候选 (sandbox-runnable):
- task020 — M1 eval basket full extension (HMMT / HLE / SciCode 等等)
- 之前 task 的 Session 2+ — 大都需 cluster
