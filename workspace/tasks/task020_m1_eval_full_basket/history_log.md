# task020 - history_log

## Session 1 — 2026-05-19 — eval basket full extension (11 rows)

### Scope

Roadmap §1.7 task020 第一个 sandbox-runnable session — 把 M1 eval
basket 从 v0 8 个扩到 plan §5.7 全 19 个。复用 task019 Session 1 的
`eval_basket_registry` schema kind，row shape 完全一样，整个扩展是
"append 11 rows + 加新索引 entry + 加新 NeMo Evaluator config" — 不
碰 schema 代码。

### Done

1. 新 file `m1_eval_basket/m1_eval_full_basket_registry.yaml`:
   - HMMT (cc-by-sa-4.0, reasoning_math_competition, pass_at_1)
   - HLE (cc-by-4.0, reasoning_extreme_difficulty, accuracy)
   - SciCode (apache-2.0, code_scientific, pass_at_1)
   - TerminalBench (apache-2.0, tool_use_terminal, success_rate)
   - SWE-Bench Verified (cc-by-4.0, swe_repo_repair, resolution_rate)
   - AA-LCR (cc-by-4.0, long_context_qa, accuracy)
   - MMLU-ProX (mit, multilingual_reasoning, accuracy)
   - WMT24++ (cc-by-4.0, multilingual_translation, bleu)
   - BFCL (apache-2.0, tool_use_function_call, accuracy)
   - MCP-Mark (apache-2.0, tool_use_mcp, success_rate)
   - Tool Decathlon (cc-by-4.0, tool_use_agentic, weighted_score)

2. `data_registries/unified_index.yaml` 加 `m1_eval_full_basket` entry
   (kind `eval_basket_registry` — 复用 task019 的 kind，没有新 KNOWN_KINDS)

3. `stage3_eval/config/m1_full_basket.yaml` 选 19 个 task (v0 8 + full
   11)，task name 按 `adlr_<benchmark_id>` 约定，order 按 category 分组
   便于阅读

4. 14 个 pytest case in `test_m1_eval_full_basket.py`:
   - Registry shape 4: 11 rows / 必填字段 / HMMT CC-BY-SA / adapter
     convention `nemo_evaluator.<benchmark_id>`
   - No-overlap 2: v0 ∩ full == ∅ / v0 ∪ full == 19 distinct
   - Schema integration 3: unified index entry / live validate clean /
     KNOWN_KINDS 保持 7
   - m1_full_basket.yaml 3: 合法 yaml / 19 tasks / task name 与 registry
     benchmark_id 完全 cross-walk
   - regression_report 2: 合并 gate map 下 diff_eval_runs 正常工作 /
     每个 full row 的 gate_metric 在合并 map 里能找到

### Test counts

- 14 new tests; sandbox 测试基线 **357 → 371 passed + 7 skipped** (14 new)
- `test_m1_agentic_sft.py` 仍然 pyarrow ImportError，pre-existing 跟本 PR 无关

### Decisions

- **复用 task019 schema kind 而非加 `eval_full_basket_registry` 新 kind** —
  row shape 完全一样，加 kind 是无用 surface 增长。Session 1 测试明确
  lock KNOWN_KINDS 在 7 防 future drift
- **两个 registry 文件而非单个 19-row 文件** — 保持 v0 vs full 边界
  显式，便于 Session 2 promotion gate 单独处理 v0 (minimum signal) vs
  full (parity breadth) — 也对 license cascade audit 友好 (HMMT 跟
  AIME25 一样 CC-BY-SA，但 audit 分别按 registry 给报告)
- **`m1_full_basket.yaml` 全选 19 task** — 不做 v0 / full 两份 config，
  操作员要跑 v0 only 用 `m1_basket.yaml`，要跑 full 用 `m1_full_basket.yaml`
- **regression_report.py 无需改** — `diff_eval_runs` 已经接 arbitrary
  `gate_metric_by_id` map，CLI 在 Session 2 合并两份 registry 给一个
  map 就行；Session 1 用 `_combined_gate_map` test helper 验证

### Deferred

- Session 2 promotion gate logic — weighted-mean Super3 parity + per-category
  regression > 1-2% + rollback rule (safety / SWE / tool / IF)。这是
  task020 的核心 deliverable，sandbox-runnable
- Session 3 cluster verify — `nemotron super3 eval -c m1_full_basket`
  真跑 + W&B publish；需 cluster + 真 SFT checkpoint
- Session 4 gap analysis — 按 plan §5.7 weighted parity 给 per-category
  报告，sandbox-runnable，但 layer on Session 2

### task030 不再相关

task020 Session 1 复用 task019 加的 schema kind，本 PR 不动 task030
任何东西。task030 已经全部 Sessions 落地。


## Session 2 — 2026-05-19 — promotion gate logic

### Scope

Plan §5.7 / roadmap §1.7 task020 promotion gate logic — weighted-mean
Super3 parity + per-category regression threshold + rollback rule
(safety / SWE / tool / IF)。Sandbox-runnable，所有 input 是 dict，
output 是 dataclass + markdown report。

### Done

1. 新 module `m1_eval_basket/promotion_gate.py`:
   - 4 个 default constants:
     - `DEFAULT_WEIGHTED_PARITY_THRESHOLD = 0.02` (2%)
     - `DEFAULT_CATEGORY_REGRESSION_THRESHOLD = 0.02` (2%)
     - `DEFAULT_ROLLBACK_REGRESSION_TOLERANCE = 1e-4`
     - `DEFAULT_ROLLBACK_CATEGORIES` frozenset (swe / tool_use_*  /
       instruction_following / multi_turn_instruction / safety_*)
   - `GATE_STATUSES = ("promote", "hold", "rollback")`
   - `PromotionDecision` frozen dataclass + `to_jsonable()`
   - `evaluate_promotion_gate(current, super3, registry_rows, *, thresholds, rollback_categories)`:
     - Group benchmarks by category，calculate per-category mean (skip
       categories where either side lacks all benchmarks)
     - Weighted parity = mean of per-category deltas (uniform across
       categories — 防 benchmark count gaming)
     - 三档严重度：rollback (任何 rollback-category 跌过 noise) > hold
       (非 rollback category 跌过 threshold 或 parity 超 threshold) >
       promote
     - Reasons list 记录每条触发条件，operator 能看到所有 findings
   - `format_gate_report(decision)` markdown:
     - Headline status with ✓ / ⚠ / ✗ markers
     - Weighted parity + reasons + per-category Δ table
     - Missing-benchmarks section 仅在 non-empty 时出现

2. 21 个 pytest case in `test_promotion_gate.py`:
   - Constants 3: status tuple / default thresholds / rollback categories cover swe/tool/if
   - Promote 2: exact match / within parity threshold
   - Hold 3: overall parity drift / non-rollback category regression
     (general_mc) / 净正 drift > threshold
   - Rollback 5: SWE / IF / tool_use / precedence over hold /
     tolerance absorbs noise
   - Weighting 1: uniform per-category not per-benchmark (TOY_ROWS 有
     2 个 reasoning_math rows，确认不被 over-weight)
   - Missing 2: missing-in-current 不阻塞 / no shared categories → hold
   - Formatting 3: promote / rollback with reasons / missing-benchmark
     section
   - Integration 2: live 19-row basket happy promote / full-basket SWE
     row regression triggers rollback

### Test counts

- 21 new tests; sandbox 测试基线 **371 → 392 passed + 7 skipped** (21 new)

### Decisions

- **三档严重度 vs 二档 (promote / no-promote)** — plan §5.7 显式分 hold
  vs rollback，rollback 不只是 "fail gate" 而是 "revert to prior
  checkpoint"。Separating them lets the operator know whether a hold
  is recoverable (re-train + retest) or whether the run was actively
  worse than the prior baseline (must roll back)
- **Default 2% threshold (tight end of plan's "1-2%")** — 2% 比 1%
  宽容，但 plan 显式提 1-2% range；选 2% 让正常的 sampling noise 不至
  于触发 hold。Operator 可以收紧到 1% 走更严格 gate
- **Uniform-per-category weighting** — plan §5.7 没显式说，但 "weighted
  mean" 在多种解读里，per-benchmark uniform 会被 reasoning_math 这种
  2-benchmark category over-weight。Uniform-per-category 更 stable，
  且未来 basket 扩展时不会改变 category 的相对权重
- **Forward-compatible safety categories in rollback set** — M1 没有
  safety benchmark，但 plan §5.7 显式 list safety 在 rollback 条件
  里。提前把 `safety` / `safety_jailbreak` / `safety_overrefusal` 加
  进 DEFAULT_ROLLBACK_CATEGORIES，M2 加 safety rows 时自动走 rollback
  path 而不需要改 gate 代码
- **Rollback tolerance 1e-4 same as regression_report** — eval runs
  aren't bit-exact；这个 noise band 是 SAMPLING_TOLERANCE 的一部分。
  跟 `regression_report.DEFAULT_REGRESSION_TOLERANCE` 对齐
- **Missing benchmarks don't auto-block** — 让 operator 看到 coverage
  gap (在 reasons 里 + missing 列表)，但不自动 hold；运行者可以选
  跑部分 basket (e.g., 只跑 v0 8 个) 而不被 gate 拒绝

### Deferred

- Session 3 (cluster verify) — `nemotron super3 eval -c m1_full_basket`
  真跑 + W&B publish；需 cluster + 真 SFT checkpoint + 真 Super3 baseline
- Session 4 (per-category gap analysis tooling) — layer on top of
  Session 2，给 per-category weighted parity 报告 + 历史 trend
  visualization。Sandbox-runnable 但需要 Session 3 真数据来做有意义的
  调试

### task019 互动

task019 Session 4 acceptance ("promotion gate logic — read
regression_report deltas, decide promote/hold per plan §5.7") 跟
task020 Session 2 完全重叠。本 PR 提供的 `promotion_gate.py` 是
task019 Session 4 的实现 — 数据层 (task019 v0 + task020 full) +
gate logic (task020 Session 2) 一起完成 plan §5.7 acceptance。

不显式 close task019 Session 4 — task019 整 task 还有 Session 2/3
(cluster verify + per-benchmark adapter)，等那些落地后再统一 closeout。


## Session 4 — 2026-05-19 — per-category gap analysis tooling

### Scope

Roadmap §1.7 task020 Session 4 — per-category gap analysis tooling。
跟 Session 2 promotion_gate 互补：promotion_gate 给 binary 决策，
gap_analysis 给 prescriptive ranking 告诉 operator "下一轮训练 focus
哪里"。Sandbox-runnable，跟 Session 2 同样 input shape。

### Done

1. 新 module `m1_eval_basket/gap_analysis.py`:
   - `DEFAULT_GAP_THRESHOLD = 0.02` (matches Session 2 / plan §5.7
     "1-2 %" tight end so "behind" in gap_analysis 跟 "in regression"
     in promotion_gate 对齐)
   - `BenchmarkGap` frozen dataclass: benchmark_id / current /
     super3 / gap (gap = current - super3 or None when 一侧 missing)
   - `CategoryGap` frozen dataclass: category / current_mean /
     super3_mean / gap / benchmark_gaps (sorted worst-first)
   - `analyze_gaps(current, super3, registry_rows)`:
     - Group benchmarks by category
     - Per-category mean excludes missing benchmarks (partial coverage
       不被零拖下)
     - Per-benchmark drill-down sorted by gap ascending
     - Categories sorted: computable gaps first (worst gap first)，
       uncomputable gaps (None) last for stability
   - `count_categories_below_threshold(gaps, *, threshold)` — summary
     line helper; skips uncomputable gaps (没数据不算 "behind")
   - `format_gap_analysis(gaps, *, threshold)` markdown:
     - Headline + summary line (X categories more than Y% behind)
     - Ranked category table with status column (behind / on par /
       ahead / no data)
     - Drill-down section ONLY for below-threshold categories
       (clean runs don't get noisy drill-down)

2. 17 个 pytest case in `test_gap_analysis.py`:
   - Dataclass surface 2: threshold default / BenchmarkGap optional values
   - Single-category 3: per-category gap rows / two-benchmark mean math /
     per-benchmark drill-down sorted worst-first
   - Multi-category ranking 2: worst-gap-first / uncomputable gaps to end
   - Missing benchmarks 2: gap=None when 一侧 missing / mean excludes missing
   - count_categories_below_threshold 2: only computable gaps counted /
     respects custom threshold
   - format_gap_analysis 4: summary+table / drill-down for behind /
     empty input / no drill-down when all on par
   - Live integration 2: 19-row basket happy on par / worst-category-first
     for full-basket regression

### Test counts

- 17 new tests; sandbox 测试基线 **392 → 409 passed + 7 skipped** (17 new)

### Decisions

- **不跟 promotion_gate 共代码** — 模块边界清晰：promotion_gate 给
  binary 决策，gap_analysis 给 ranking + drill-down。两个都做 category
  grouping 但目的不同；强行抽公共 helper 是 premature abstraction，
  尤其因为 promotion_gate 的 category grouping 输出是
  `dict[category, list[bid]]` 而 gap_analysis 需要 per-benchmark drill-
  down 保留 score。
- **Worst-first sorting (gap ASCENDING)** — operator workflow 是 "我
  现在看 report，先解决最痛的"，所以 most negative gap 在最上面。
  promotion_gate 的 `format_gate_report` 用 category_deltas dict 的
  字母序 (稳定 diff)，但 gap_analysis 是给 *人* 看的，priority order
  更有意义
- **Drill-down only for below-threshold categories** — 一份健康的 run
  应该出健康的 report。把所有 19 个 category 都做 drill-down 会让
  报告吵；只 surface 真正需要关注的让 report 是 actionable signal。
  内部测试 `test_format_gap_analysis_omits_drill_down_when_all_on_par`
  lock 这个 behavior
- **`count_categories_below_threshold` 是 public helper** — 操作员
  pipeline 可能想直接拿这个 count 做 alerting，不需要 parse markdown。
  把它 export 出来比 inline 在 format 函数里好
- **Uncomputable gaps don't count as "behind"** — 一个 category 没数
  据 ≠ "需要 focus"；它是 "需要先确认 eval 跑全了"。所以
  count_categories_below_threshold 跳过 None gap，但 markdown 报告
  仍然 surface 它 (status="no data") 给 operator 看见

### Deferred

- Session 3 (cluster verify) 仍是 task020 最后一个 todo — `nemotron
  super3 eval -c m1_full_basket` 真跑 + W&B publish + 真 Super3 baseline
  numbers。需 cluster + 真 SFT checkpoint
- task019 Session 2/3 (cluster-side wiring + per-benchmark adapter
  configs)

### task019 / task020 互动

- task019 Session 4 (promotion gate logic) — 由 task020 Session 2 提供
- task020 Session 4 (gap analysis) — 本 PR
- task019 / task020 现在 sandbox 部分都落地：
  - 数据层：task019 Session 1 (v0 8 rows + eval_basket_registry schema
    kind) + task020 Session 1 (full 11 rows + combined config)
  - Analysis layer：regression_report (vs prior) + promotion_gate
    (gate decision) + gap_analysis (prescriptive ranking)
- 剩下 cluster-side wiring 一份 PR 把三个模块接到 `nemotron super3
  eval` CLI，等 cluster access
