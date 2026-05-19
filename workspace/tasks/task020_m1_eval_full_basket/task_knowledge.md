# task020 - task_knowledge

## Plan §5.7 acceptance basket (v0 + full)

19 benchmarks split across categories per plan §5.7 / roadmap §1.7:

| Category | v0 rows (task019) | Full extension rows (task020) |
|---|---|---|
| general_mc | mmlu_pro | — |
| reasoning_math_competition | aime25 | **hmmt** |
| reasoning_graduate_science | gpqa | — |
| reasoning_extreme_difficulty | — | **hle** |
| code_competitive_programming | livecodebench | — |
| code_scientific | — | **scicode** |
| instruction_following | ifbench | — |
| multi_turn_instruction | multichallenge | — |
| long_context | ruler_256k | — |
| long_context_qa | — | **aa_lcr** |
| tool_use_agentic | taubench_airline | **tool_decathlon** |
| tool_use_terminal | — | **terminalbench** |
| tool_use_function_call | — | **bfcl** |
| tool_use_mcp | — | **mcp_mark** |
| swe_repo_repair | — | **swe_bench_verified** |
| multilingual_reasoning | — | **mmlu_prox** |
| multilingual_translation | — | **wmt24pp** |

Total v0 = 8, full extension = 11, combined = 19.

## License posture for full rows

| benchmark_id | license | eval-time signal |
|---|---|---|
| hmmt | cc-by-sa-4.0 ⚠ | mirrors AIME25 — informational |
| hle | cc-by-4.0 | clean |
| scicode | apache-2.0 | clean |
| terminalbench | apache-2.0 | clean |
| swe_bench_verified | cc-by-4.0 | clean |
| aa_lcr | cc-by-4.0 | clean |
| mmlu_prox | mit | clean |
| wmt24pp | cc-by-4.0 | clean |
| bfcl | apache-2.0 | clean |
| mcp_mark | apache-2.0 | clean |
| tool_decathlon | cc-by-4.0 | clean |

Only HMMT joins AIME25 as a share-alike row. task058 license cascade
audit will flag both; eval-time use does not cascade share-alike onto
checkpoints (same eval-vs-training distinction noted in task019
Session 1).

## Adapter naming convention

Every adapter follows ``nemo_evaluator.<benchmark_id>`` so the
schema-layer audit can cross-walk config selectors and registry rows
without ambiguity. Same as v0; locked in
``test_full_basket_adapter_names_match_benchmark_ids``.

NeMo Evaluator task name follows ``adlr_<benchmark_id>`` (mirrors
existing ``stage3_eval/config/default.yaml`` adapter set). Same as v0;
locked in ``test_full_basket_config_task_names_match_registry_benchmark_ids``.

## Why two registry files, not one merged

- v0 (8) = minimum signal needed to gate the M1 → M2 promotion. Small,
  fast, cheap to run on every checkpoint.
- Full (11) = breadth needed for the plan §5.7 weighted-parity decision
  vs Super3. Larger, includes longer-running benchmarks (TerminalBench,
  SWE-Bench Verified, RULER long context).

Operators run ``m1_basket.yaml`` for quick smoke / regression checks and
``m1_full_basket.yaml`` for parity gates. Keeping them as two
registries makes the v0 / full distinction explicit in the data layer.

## Why no new schema kind

`eval_basket_registry` (from task019 Session 1) already declares the
required shape ``(benchmark_id, adapter, category, license,
gate_metric)``. The full extension uses the same shape — adding a new
KNOWN_KINDS entry would be pure surface growth without semantic
benefit. Locked in ``test_full_basket_uses_existing_eval_basket_registry_kind``
which asserts ``len(KNOWN_KINDS) == 7``.

## regression_report.py — combined gate map

`diff_eval_runs(current, baseline, gate_metric_by_id)` accepts an
arbitrary string→string map. Session 2 CLI will build the combined map
by merging both registries' rows (no conflict resolution needed since
benchmark_ids don't overlap — locked in
``test_full_basket_does_not_redefine_any_v0_benchmark``).

Session 1 has a `_combined_gate_map()` test helper that does exactly
this merge, so the regression report path is exercised end-to-end
without needing the CLI yet.

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| Registry shape + schema integration | yes |
| No-overlap with v0 | yes |
| m1_full_basket.yaml selector cross-walk | yes |
| regression_report against combined gate map | yes |
| Session 2 promotion gate logic (weighted parity + thresholds) | yes |
| Session 3 真 `nemotron super3 eval -c m1_full_basket` 启动 | no |
| Session 4 gap analysis tooling (depends Session 2 + 真数据) | partial |

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 仍因 pyarrow ImportError
collect-error，pre-existing；非 sandbox 正常跑。运行 sandbox 测试时用
`--ignore=tests/recipes/super3/test_m1_agentic_sft.py`。

## Promotion gate decision model (Session 2)

Per plan §5.7 + roadmap §1.7 task020 promotion gate text:

> Promotion gate logic: weighted-mean Super3 parity, no key-category
> regression > 1-2 %, rollback rule on safety / SWE / tool / IF.

### Three-tier severity

| Status | When | Operator action |
|---|---|---|
| `promote` | All checks pass | Ship the checkpoint |
| `hold` | Parity drifts > 2% OR non-rollback category regresses > 2% OR coverage gap (no shared categories) | Re-train / retest with diagnosis |
| `rollback` | Any rollback-category drops beyond noise (1e-4) | Revert to prior checkpoint |

Severity precedence: rollback > hold > promote (most severe wins).
Reasons list records *all* triggered conditions, not just the
tipping one.

### Default thresholds (`promotion_gate.py`)

- `DEFAULT_WEIGHTED_PARITY_THRESHOLD = 0.02` (2% — plan's "1-2%" tight end)
- `DEFAULT_CATEGORY_REGRESSION_THRESHOLD = 0.02` (2%)
- `DEFAULT_ROLLBACK_REGRESSION_TOLERANCE = 1e-4` (sampling noise)
- `DEFAULT_ROLLBACK_CATEGORIES` (frozenset):
  - `swe_repo_repair`
  - `tool_use_agentic` / `tool_use_terminal` / `tool_use_function_call` / `tool_use_mcp`
  - `instruction_following` / `multi_turn_instruction`
  - `safety` / `safety_jailbreak` / `safety_overrefusal` (forward-compat M2)

### Weighting policy

**Uniform-per-category, uniform-across-categories**. Each category
gets equal weight regardless of how many benchmarks it contains.

Why not per-benchmark? `reasoning_math_competition` has 2 benchmarks
(AIME25 + HMMT) but `general_mc` has 1 (MMLU-Pro). Per-benchmark
uniform would let any category with extra rows dominate parity
swings. Per-category uniform is stable under future basket extension.

### Missing benchmark handling

- Missing in current run: noted in `benchmarks_missing_in_current`,
  the category is dropped from parity calc, gate **does NOT auto-hold**
- Missing in Super3 baseline: noted in `benchmarks_missing_in_super3`,
  same handling — operator decides
- No shared categories at all: parity is `None`, gate holds with a
  specific reason. Prevents silent promote on empty/broken eval JSON.

### Interaction with regression_report.py

`promotion_gate.py` and `regression_report.py` answer different
questions:

- **regression_report**: how did this run compare to the prior
  checkpoint? (per-benchmark diff + status: improved / regressed / etc.)
- **promotion_gate**: is this run good enough to promote vs Super3?
  (per-category aggregate + parity threshold + rollback rule)

Both can be run on the same eval JSON; they share no code today but
could share a `current_results` extraction helper in the future.
