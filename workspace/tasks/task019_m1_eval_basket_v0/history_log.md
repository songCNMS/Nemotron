# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-19 - intern_nemontron_review_cc

由 roadmap §1.7 / §5 critical-path 第 9 条派生。task019 整 task：M1 eval
basket v0 — 8-benchmark registry + NeMo Evaluator launcher + regression
report。

## Session 1 - 2026-05-19 - intern_nemontron_review_cc

实现 M1 eval basket scaffold (sandbox-runnable; 真 launch 留 Session 2+)。

设计要点:

- 新模块 `m1_eval_basket/`，跟其他 milestone 模块平级
- `m1_eval_basket_registry.yaml` 8 行严格按 plan §5.7 v0 列表 (MMLU-Pro /
  AIME25 / GPQA / LiveCodeBench / IFBench / MultiChallenge / RULER 256K /
  TauBench airline)。每行 `benchmark_id` / `adapter` / `category` /
  `license` / `gate_metric` / `notes`
- AIME25 license 标 cc-by-sa-4.0 — task058 license cascade audit
  (Session 5) 会 pick up 这条；notes 里明确 eval-time 用 vs training-time
  inheritance 区别 (legal 确认 eval report 不传 share-alike 到 checkpoint)
- 新 schema kind `eval_basket_registry` 加进 `data_registries/schema.py`
  (`rows_key: benchmarks`, required fields: benchmark_id / adapter /
  category / license / gate_metric)。KNOWN_KINDS 6 → 7
- `unified_index.yaml` 加 `m1_eval_basket` entry; `_ROWS_KEY_BY_KIND` 和
  `_row_identity` 加分支
- `regression_report.py` 纯 stdlib + yaml 实现:
  - `BenchmarkDelta` dataclass — benchmark_id / metric / baseline /
    current / delta / status
  - `load_eval_results(path)` — 读 NeMo Evaluator JSON
  - `diff_eval_runs(current, baseline, gate_metric_by_id, tolerance)` —
    5 个 status: improved / regressed / unchanged (within tolerance) /
    new (only in current) / dropped (only in baseline)
  - `format_regression_report(deltas)` — markdown 输出，状态 marker
    (↑ ↓ · + -)，sorted by benchmark_id for stable diff
- `stage3_eval/config/m1_basket.yaml` — NeMo Evaluator config:
  - `defaults: default.yaml` 继承 executor + deployment 设置
  - `tasks:` 8 个 task name (adlr_ 前缀)，suffix 匹配 benchmark_id

**task030 Session 3 自动 unblock**: 之前多次 closeout 把 task030 Session
3 标 "block on task019/020 给 eval basket 真定义"。本 PR 给定义 + 新
kind + index 接入；task030 Session 3 acceptance 已在这条 PR 一并达成。

测试 `tests/recipes/super3/test_m1_eval_basket.py` 22 case:

- Registry shape 3: 8 row 正好 / required fields 全有 / AIME25 license
  锁 cc-by-sa-4.0
- Schema integration 3: KNOWN_KINDS 含 eval_basket_registry / unified
  index 含 m1_eval_basket / live unified validate clean
- load_eval_results 2: 加载正常 / 拒 missing tasks key
- diff_eval_runs 8: improved / regressed / unchanged (tolerance) /
  new / dropped / 不在 gate map → 跳 / None 值 → 跳 / 排序稳定
- format_regression_report 3: 空 deltas / summary count / em-dash for
  new+dropped
- m1_basket.yaml 3: 合法 yaml / defaults: default.yaml / 8 task name 匹配 registry

修了一处 hardcoded 测试 (`test_known_kinds_covers_today_registry_families`)
加上第 7 个 kind。

测试基线 335 → 357 passed + 7 skipped (22 new).

## Session 2+ 不在本 PR

- Session 2 (cluster verify) — 真 `nemotron super3 eval -c m1_basket`
  跑 + W&B publish
- Session 3 (per-benchmark adapter configs) — 每个 NeMo Evaluator adapter
  可能要自己的 config，ops 协作
- Session 4 (promotion gate) — 读 regression_report 自动决定 promote/hold
