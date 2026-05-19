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
