# task020_m1_eval_full_basket

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #72 / deec7b7 on 2026-05-19 (11-row full basket extension + m1_full_basket.yaml config) -->
<!-- SESSION 2 LANDED: PR #74 / 33b51e7 on 2026-05-19 (promotion gate logic — weighted-mean parity + per-category regression + rollback rule) -->
<!-- SESSION 4 LANDED: PR #76 / 44c5ec8 on 2026-05-19 (per-category gap analysis tooling — ranked category gap + per-benchmark drill-down) -->

## 背景

`docs/implementation-roadmap.md` §1.7 / §5 critical-path #10:

> task020_m1_eval_full_basket — add the rest:
> - HMMT, HLE, SciCode, TerminalBench, SWE-Bench Verified, AA-LCR,
>   MMLU-ProX, WMT24++, BFCL, MCP-Mark, Tool Decathlon.
> - Promotion gate logic: weighted-mean Super3 parity, no key-category
>   regression > 1-2 %, rollback rule on safety / SWE / tool / IF (per
>   plan §5.7 promotion gate).

整 task 拆 Sessions:

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | 11-row full basket extension + `stage3_eval/config/m1_full_basket.yaml` 选 19 个 tasks | yes | ✓ Done (PR #72) |
| 2 | Promotion gate logic — weighted-mean Super3 parity + per-category regression > 1-2 % threshold + rollback rule (safety / SWE / tool / IF) | yes | ✓ Done (PR #74) |
| 3 | CLI wiring `nemotron super3 eval -c m1_full_basket` 真跑 + W&B publish | no — cluster + checkpoint | Todo |
| 4 | Per-category gap analysis tooling (跟 plan §5.7 weighted parity 对齐) | yes (depends Session 2) | ✓ Done (this PR) |

## Session 1 目标

- `m1_eval_basket/m1_eval_full_basket_registry.yaml` 11 rows (HMMT /
  HLE / SciCode / TerminalBench / SWE-Bench Verified / AA-LCR /
  MMLU-ProX / WMT24++ / BFCL / MCP-Mark / Tool Decathlon)
- 复用 task019 `eval_basket_registry` schema kind — *不* 加新 kind
- `unified_index.yaml` 加 `m1_eval_full_basket` entry
- `stage3_eval/config/m1_full_basket.yaml` 选 19 个 task (v0 8 + full 11)
- 14 个 pytest case (registry shape / 11 rows / 必填字段 / HMMT
  CC-BY-SA / adapter convention / no overlap with v0 / schema
  integration / KNOWN_KINDS 不增长 / 合法 yaml / 19 tasks / config-registry
  cross-walk / combined gate_metric_by_id 跑 diff)

## Session 1 验收

- [x] 新 file `m1_eval_full_basket_registry.yaml` 11 rows
- [x] `unified_index.yaml` 加 `m1_eval_full_basket` entry；validate clean
- [x] `stage3_eval/config/m1_full_basket.yaml` 选 19 个 benchmark task
- [x] v0 + full 共 19 个 distinct benchmark_id；no overlap
- [x] KNOWN_KINDS 保持 7 (复用 task019 的 kind)
- [x] regression_report.diff_eval_runs 在合并 gate map 下正常工作
- [x] 14 个 pytest case；sandbox 测试基线 357 → 371 passed + 7 skipped

## Session 2 目标

- `m1_eval_basket/promotion_gate.py` 新模块:
  - `PromotionDecision` dataclass (status / weighted_parity_delta /
    category_deltas / categories_in_regression / rollback_triggers /
    benchmarks_missing_in_current / benchmarks_missing_in_super3 / reasons)
  - `evaluate_promotion_gate(current, super3, registry_rows, *, thresholds, rollback_categories)`
  - 三档严重度 promote / hold / rollback (rollback > hold > promote)
  - Default thresholds = 2% (per plan §5.7 "within 1-2%")
  - Default rollback categories = swe_repo_repair / 全部 tool_use_* /
    instruction_following / multi_turn_instruction (+ safety_* 前向
    兼容 M2)
  - 加权策略：uniform within category, uniform across categories
    (防 benchmark count gaming)
  - `format_gate_report(decision)` markdown 输出
- 21 个 pytest case in `test_promotion_gate.py`

## Session 2 验收

- [x] 新 `promotion_gate.py` 模块 + 4 个 default constants + `GATE_STATUSES`
- [x] `PromotionDecision` dataclass + `to_jsonable()`
- [x] `evaluate_promotion_gate` 三档严重度精确实现
- [x] Weighting policy uniform-per-category (不是 per-benchmark)
- [x] Missing benchmark 不挂掉 gate
- [x] No shared categories → hold + 显式 reason
- [x] Rollback tolerance 吸收浮点噪声
- [x] `format_gate_report` markdown output
- [x] 21 个 pytest case；sandbox 测试基线 371 → 392 passed + 7 skipped

## Session 4 目标

- `m1_eval_basket/gap_analysis.py` 新模块:
  - `BenchmarkGap` dataclass: benchmark_id / current / super3 / gap
  - `CategoryGap` dataclass: category / current_mean / super3_mean /
    gap / benchmark_gaps (sorted per-benchmark)
  - `analyze_gaps(current, super3, registry_rows)` 返回 worst-first
    ranking
  - `count_categories_below_threshold(gaps, *, threshold)` 计数
    actionable categories
  - `format_gap_analysis(gaps, *, threshold)` markdown:
    - Ranked category table (worst-first)
    - Drill-down section for categories below threshold (per-benchmark
      contributions, worst-first)
- 17 个 pytest case in `test_gap_analysis.py`

## Session 4 验收

- [x] 新 `gap_analysis.py` 模块 + 1 const + 2 dataclass + 3 function
- [x] `analyze_gaps` 排序 worst-first; uncomputable gaps 排末尾
- [x] Per-benchmark drill-down 排序 worst-first within category
- [x] Missing benchmarks 不挂掉 analyze；mean 计算排除 missing 一侧
- [x] `format_gap_analysis` headline / table / drill-down 分段输出
- [x] Drill-down 仅在有 below-threshold categories 时出现 (clean run
  报告 clean)
- [x] 17 个 pytest case；sandbox 测试基线 392 → 409 passed + 7 skipped

## 模块互补关系

- `regression_report.py` — "did this run improve vs prior checkpoint?"
  (per-benchmark deltas + 5 status: improved / regressed / unchanged /
  new / dropped)
- `promotion_gate.py` — "is this run good enough to promote?"
  (per-category aggregate + 三档 binary 决策 + rollback rule)
- `gap_analysis.py` — "where should next training run focus?"
  (prescriptive ranking + per-benchmark drill-down vs Super3)

三个模块同样的输入 shape (`current_results` dict + `super3_baseline`
dict + `registry_rows`)，operator 跑一份 eval JSON 出三份 report，
回答三个不同的问题。

## 依赖

- 不依赖 cluster / W&B / 真 SFT checkpoint
- 依赖 task019 Session 1 (eval_basket_registry kind + 索引接入)
- 依赖 task020 Session 1 (full basket registry 接进来给 19-row 集成测试)
- Session 3 (CLI 真跑) 依赖 cluster + NeMo Evaluator + W&B
- Session 4 (gap analysis) 依赖 Session 2 + 真数据

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_eval_basket/` — 本 task Session 1 产物 (full registry)
- `src/nemotron/recipes/super3/milestones/data_registries/{schema.py,unified_index.yaml,unified_index_loader.py}` — schema 复用
- `src/nemotron/recipes/super3/stage3_eval/config/{default,m1_basket,m1_full_basket}.yaml` — NeMo Evaluator config
- plan §5.7 + roadmap §1.7 / §5
