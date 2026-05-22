# M2 Implementation Plan

Last updated: 2026-05-21 — refreshed after a 12-PR parallel landing
(see §10 below) by `intern_nem_dev_1/2/3` brought all 8 M2
environment-expansion Session 1's plus 4 of 6 M2 infra Session 1's
in. Sandbox baseline 829 → **934 passed + 7 skipped** (+105 tests).
Originally drafted 2026-05-20 from `docs/multi-environment-rl-post-training-plan.md`
§3 M2 milestone + `docs/implementation-roadmap.md` §2 M2 fanout.

## 0. Goal & schedule

Per PRD §3 (Milestones) and §4 (Execution Schedule):

- **Goal**: Match Qwen/Qwen3.5-122B-A10B on the chosen text / agentic /
  coding basket — weighted parity, no single critical category > 3-5%
  behind.
- **Window**: 2026-08-01 → 2026-10-16 (11 weeks).
  - 2026-08-01 → 08-31 (4 wk): Environment Expansion sprint.
  - 2026-09-01 → 10-16 (6 wk): M2 Training Sprint.
- **Acceptance basket** (PRD §3 M2 row): MMLU-Pro, GPQA, HLE,
  LiveCodeBench, SWE-Bench Verified, IFBench, MultiChallenge,
  AA-LCR / LongBench, TerminalBench, TauBench.
- **Promotion gate**: weighted-mean parity vs Qwen3.5-122B-A10B with
  no critical-category regression > 3-5%. Reuses the M1 promotion
  gate (`task020/promotion_gate.py`) with a 122B-class baseline
  swapped in (per-category thresholds tightened from the M1 numbers).

**Status snapshot (2026-05-21)**: 12 of 17 M2 tasks have Session 1
landed in main (sandbox scaffolds; no cluster work yet). Detailed
breakdown in §10. The unbuilt-today framing in this plan now applies
to **Sessions 2+** for the 12 landed tasks (bridge wiring + cluster
verification + production hardening) plus the **5 task scaffolds
still missing** (task031 Agentic SFT v1, task033 env scheduler,
task034 judge pool, task038 RL curriculum, task039 eval basket).

---

## 1. Predecessor closure required before M2 kickoff

M2 builds on the M1 stack. The following M0/M1 work is still
outstanding and gates the M2 sprint. Group A is blocking; Group B
should land in parallel with M2 environment expansion.

### Group A — hard blockers (must land before 2026-08-01)

| ID | Session | Why blocking | Class |
|---|---|---|---|
| task021 | 4 | NeMo-RL / Ray / vLLM / NeMo-Gym launch path validated end-to-end. M2 env scheduler (task033) wraps task021's launch path. | cluster |
| task014 | 2 (cluster) | RLVR data bridge real-cluster smoke. M2 dynamic-sampling curriculum (task038) needs working RLVR run. | cluster |
| task017 | 3 | SWE2 cluster smoke + Docker fallback. M2 SWE multi-harness (task026) extends task017's bridge. | cluster |
| task018 | 3 + 4 | GenRM service deployment + end-to-end RLHF from SWE2 checkpoint. M2 judge pool (task034) generalizes the GenRM router; M2 reward calibration depends on a live judge. | cluster |
| task019 | 2-3 | M1 eval basket cluster run + W&B publish. M2 eval basket (task039) extends task019's adapter configs. | cluster |
| task020 | 3 | Full 19-benchmark basket cluster run. M2 promotion gate inherits task020/promotion_gate.py + gap_analysis.py. | cluster |
| task070 | 2-3 | Real OpenHands library + SIF integration. M2 SWE multi-harness (task026) needs the production loop, not the fake. | cluster |
| task069 | 2-3 | W&B credentials + end-to-end lineage publish. M2 rollout store (task032) writes to the lineage stream. | cluster |

### Group B — parallel-ok (land alongside M2 env expansion)

| ID | Session | Notes | Class |
|---|---|---|---|
| task013 | 2b | Two-stage SFT cluster verify in nvcr Megatron-Bridge. Becomes the SFT loss recipe used by Agentic SFT v1 (task031). | cluster |
| task016 | 3 | SWE1 cluster smoke. SWE1 stays in the M1 mix; M2 SWE work focuses on SWE2 multi-harness expansion (task026). | cluster |
| task056 | 2 (cluster) | Lean verifier runtime container. Required only if M3 Lean envs are kept; M2 doesn't strictly need it. | cluster |
| task057 | 1.5 / 2.5 / 3.5 / 4.5 / 5.5 / 6.5 | data_registry SHA pins for all six tier-2 M0 envs. Required only if M2 RL mix wants to pull these envs back into training; M1 RLVR uses them via the existing env IDs. | HF access |

**Net read**: roughly 12 cluster-bound sessions sit between today
and M2 kickoff. Without NemTron access these don't drain. If
parallel cluster access is constrained, the **minimum viable M2
prerequisite set** is task021 S4 → task014 S2 → task018 S3-4 →
task019 S2-3 → task020 S3 → task070 S2-3 → task069 S2 (8 sessions
on the critical path; task017 S3 + task016 S3 + task013 S2b can
land in parallel slots).

---

## 2. M2 task fanout (per roadmap §2)

17 tasks total: 8 environment expansions + 1 Agentic SFT v1 + 6 infra +
1 RL curriculum + 1 eval basket.

### 2.1 Environment expansion (PRD §4.M2 — 35-50 envs target)

One task per family. Each follows the **8-point M0 wiring checklist**
(see `docs/m0-dataset-expansion-plan.md` §5) plus M1 bridge wiring
(env_registry + bridge `prepare_*.py` + lineage publish).

| Task | Family | M0 envs needed | Verifier work | S1 status |
|---|---|---|---|---|
| **task022** | browser / search | `browser_qa`, `browsecomp_grounded` | Playwright sandbox + grounded-answer verifier | ✓ S1 landed (offline `browser_grounded_answer_stub`; both envs registered) |
| **task023** | TauBench multi-domain | `taubench_retail`, `taubench_telecom` (airline lives in M1) | Reuse `tool_schema_and_argument_match` + multi-turn rollout | ✓ S1 landed (both envs + converter scaffold) |
| **task024** | BIRD / text-to-SQL execution | Promote `sql_text_to_query` from M0 stub → real DB sandbox env `sql_execution` | New `sql_execution` verifier (real SQLite/Postgres exec) | ✓ S1 landed (`m2_sql_execution/sqlite_verifier.py` sandbox SQLite executor + `sql_execution_mode` env field; cluster Postgres TBD) |
| **task025** | TerminalBench v2 | `terminal_workplace` longer-budget variant | Reuse `command_substring_match` + extended timeout | ✓ S1 landed (`terminal_workplace` env registered) |
| **task026** | SWE multi-harness | OpenCode + Codex agent classes alongside OpenHands (task070) | Reuse task017 sandbox runtime; add per-harness adapter | ✓ S1 landed (`m1_swe2/swe_multi_harness.py` adapter scaffold) |
| **task027** | Multilingual IF / code | `multilingual_ifeval`, `multilingual_humaneval` | Reuse `multilingual_exact_or_contains` (task057 Session 1) + new IF judge | ✓ S1 landed (both envs registered + tests) |
| **task028** | Long context | RULER 512K / 1M + AA-LCR + long-doc QA (extends task057 Session 2 `long_context_qa_smoke`) | New `long_context_qa` non-stub verifier with span-aware match | ✓ S1 landed (`long_context_ruler` + `long_context_aalcr` + `long_context_doc_qa` envs + `long_context_qa` span-aware verifier) |
| **task029** | Safety / jailbreak / over-refusal | `safety_judge`, `jailbreak_resist`, `over_refusal` (extends task057 Session 5 `safety_reasoning_smoke`) | New `safety_judge` verifier with real judge model | ✓ S1 landed (all 3 envs registered; `safety_judge_stub` verifier reused — real judge service still TBD per task034) |

**Each task is 1-2 weeks**; all depend on **task021** for infra and
on the corresponding M1 bridges. Within each family, prefer
splitting into:
- **Session 1 — converter + env_registry + verifier stub** (sandbox)
- **Session 2 — bridge wiring + lineage publish** (sandbox)
- **Session 3 — cluster smoke + W&B publish** (cluster)
- Optional **Session 1.5/...** for HF SHA pins (matches task057 pattern)

This splitting lets sandbox work proceed even when cluster access is
constrained.

### 2.2 Agentic SFT v1 — task031

PRD §6 v1 scope:
- Multi-turn tool traces with observation handling.
- Self-correction trajectories.
- Failure-repair trajectories (sourced from M1 failed rollouts).
- Cross-harness SWE traces (OpenHands + OpenCode + Codex).
- Compact / low-effort reasoning variants.

→ **task031_agentic_sft_v1**. Depends on ≥4 of task022-028 (need
multi-turn data sources) + task032 (rollout store, for failure
mining) + task070 + task026.

Suggested sessions:
1. Multi-turn supervision builder (extends `prepare_m1_agentic_sft.py`)
2. Failure-repair pipeline (read from rollout store, filter, convert)
3. Cross-harness SWE supervision routing
4. Compact-reasoning mode supervision
5. Cluster training run on Agentic SFT v1 mix
6. Eval gate against M1 baseline (no regression on M1 mix; gain on multi-turn)

### 2.3 M2 RL infrastructure — task032-037

Per PRD §10 M2 infra block:

| Task | Component | Depends on | S1 status |
|---|---|---|---|
| **task032** | Central rollout store — schema, write path, indexed retrieval keyed on `(prompt_id, model_version, env_id)`. Foundation for failure mining + dynamic sampling. | task069 lineage stream | ✓ S1 landed (`rollout_store/local_store.py` — `LocalRolloutStore` + `RolloutKey` + `RolloutTrace`, sandbox JSONL backend; production backend + W&B/lineage stream + retention policy TBD in S2+) |
| **task033** | Env scheduler — quota, backpressure, fast/slow queue split. Slow envs (SWE / browser / GUI) run on separate queue. | task032 (backpressure signal) + task021 | ✗ unscaffolded |
| **task034** | Judge service pool — model versioning + calibration sets + ensemble voting. Generalizes the GenRM router from task018. | task018 S3 (GenRM deployed) | ✗ unscaffolded |
| **task035** | Contamination pipeline + eval-overlap report — reuses task001's `contamination` field; emits a per-env overlap matrix. | task030 (unified registry done) | ✓ S1 landed (`contamination_matrix.py` reusing `classify_contamination_row` + new `--eval-overlap-matrix`/`--contamination-matrix` CLI flag on `validate_data_registries.py`; 14 M0 rows clean in live registry smoke) |
| **task036** | Canary + shadow-eval pipeline — every promoted checkpoint runs the held-out shadow split; gates promotion. | task020 promotion gate | ✓ S1 landed (`shadow_eval/pipeline.py` — `build_synthetic_shadow_plan` + `evaluate_shadow_plan` reading `LocalRolloutStore` + delegating to `evaluate_promotion_gate`; real cluster eval + W&B publish TBD in S2+) |
| **task037** | Env health dashboard — Grafana / W&B board over telemetry stream from task021/021. | task021 S2 lineage emitter | ✓ S1 landed (`m2_env_health_dashboard/dashboard.py` reading recorded `health_baseline_report.json` — slow-signal threshold + telemetry-gap detection + latency panel; Grafana/W&B board layout TBD in S2+) |

Suggested ordering: 032 → 034 (parallel with 033) → 035 (parallel
with 036) → 037 last (rides on stable telemetry stream).

### 2.4 M2 RL recipe — task038

Per PRD §7 M2:
- Per-environment quota.
- Dynamic sampling by env gap (failing envs sampled more).
- Judge ensemble for non-binary rewards.
- Per-environment reward calibration.

→ **task038_m2_rl_curriculum**. Depends on **task032** (rollout
store, for gap signal) + **task034** (judge pool, for ensemble) +
**task040 S3** (numeric pass-rate filter from W1 curriculum work,
was deferred to M2).

Suggested sessions:
1. Per-env gap estimator (reads rollout store; emits per-env weight)
2. Dynamic sampler that consumes weights (extends `task040` sampler)
3. Per-env reward calibrator (z-score normalization per env per checkpoint)
4. Judge ensemble dispatcher
5. Cluster smoke on small mix (3-5 envs)
6. Full M2 RL run

### 2.5 M2 eval expansion — task039

Per roadmap §2.5, extends task020's full basket:
- HLE
- BrowseComp
- BIRD (real execution)
- BFCL (full, not just smoke)
- MCP-Mark
- Tool Decathlon
- Multilingual IF / code / tool

→ **task039_m2_eval_basket**. Depends on task020 (gate + gap-analysis
landed) + ≥6 of task022-028 (env infrastructure for the new
benchmarks).

Suggested sessions:
1. Benchmark registry + adapter configs (sandbox)
2. Per-category gap thresholds tuned for 122B-class parity (sandbox)
3. Cluster run end-to-end on final M2 checkpoint
4. Promotion gate update — 122B baseline numbers replace Super3 numbers

---

## 3. Cross-cutting M2 carry-overs

| Item | Carry-over from | Status |
|---|---|---|
| Difficulty curriculum sampler S3 (numeric pass-rate filter) | task040 | Was explicitly deferred to M2 — depends on task032 rollout store for the pass-rate signal |
| Failure rollout → SFT repair pipeline | W1 (originally separate, folded into task031 / task047) | Lands as part of task031 sessions |
| Per-env held-out shadow split | W2 | Lands as part of task036 |
| Eval basket registry kind | task030 S3 | Already landed in task019 S1 — no carry-over |

---

## 4. Sandbox vs cluster split for M2

Each environment-expansion task has a **3-session pattern**:
sandbox converter + sandbox bridge wiring + cluster smoke. This
gives intern-on-sandbox-only roughly **~70%** of M2 env work as
sandbox-actionable (16 sandbox sessions across 8 envs), with
cluster verification batched at the end.

Infra tasks (task032-037) split similarly:
- **Sandbox-friendly**: task032 (schema + write path), task035
  (audit logic + reports), task036 (gate logic + threshold tuning),
  task037 (dashboard layout + queries; the data only needs a
  recorded telemetry stream).
- **Cluster-bound**: task033 (real scheduler), task034 (judge model
  deployment), final dashboard hookup.

RL-recipe task038 sessions 1-4 are sandbox-friendly (estimators +
samplers tested against synthetic rollout traces); sessions 5-6 are
cluster-bound.

Agentic-SFT v1 task031: data-prep + supervision builder sessions
sandbox-runnable; the training run is cluster-bound.

Eval task039 sessions 1-2 sandbox-friendly; 3-4 cluster.

---

## 5. Recommended execution order

Given current state (M1 sandbox layer complete; cluster bottleneck
unresolved), the recommended ordering is:

### Phase 0 — predecessor closure (2026-05-21 → 2026-07-31)
Drain Group A blockers as cluster access opens. Sandbox work
during this window: M2 task scaffolds + sandbox-only sessions
(see Phase 1 below; can start immediately).

### Phase 1 — M2 scaffolding + sandbox env work (parallel with Phase 0)
**Status as of 2026-05-21: largely complete** (12 of ~12 planned
PRs landed by `intern_nem_dev_1/2/3` — see §10).
1. ✓ **task022-029 Session 1** scaffolds — converters +
   env_registry entries + verifier stubs. 8 tasks × 1 session each
   = 8 PRs. **All landed.**
2. ✓ **task032 Session 1** rollout-store schema + write path.
3. ✓ **task035 Session 1** contamination eval-overlap matrix.
4. ✓ **task036 Session 1** shadow-eval pipeline.
5. ✓ **task037 Session 1** dashboard against recorded telemetry.

**Remaining Phase 1 work**: scaffold the 5 missing tasks
(task031 / task033 / task034 / task038 / task039) and start their
Session 1's where sandbox-actionable.

### Phase 2 — M2 Environment Expansion sprint (2026-08-01 → 08-31)
1. **task022-029 Session 2 + 3** — bridge wiring + cluster smoke
   per env. ~16 PRs over 4 weeks.
2. **task032 Session 2** — production rollout store deployed.
3. **task034 Session 1** — judge pool generalized from task018.
4. **task033 Session 1** — env scheduler scaffolding.

### Phase 3 — M2 Training Sprint (2026-09-01 → 10-16)
1. **task031 Sessions 1-4** — Agentic SFT v1 data + supervision
   (sandbox). **Session 5** = cluster training run.
2. **task038 Sessions 1-4** — RL curriculum logic (sandbox).
   **Sessions 5-6** = cluster smoke + full run.
3. **task033 + task034** Session 2+ — production scheduler + judge
   ensemble live.
4. **task036 + task037** — shadow-eval + dashboard live.
5. **task039** Sessions 1-2 sandbox; **Sessions 3-4** cluster.
6. **task020 promotion gate** swap: replace Super3 baseline numbers
   with Qwen3.5-122B-A10B numbers; rerun gate.

### Phase 4 — M2 freeze + gate (2026-10-10 → 10-16)
1. Final eval on M2 basket vs Qwen3.5-122B-A10B baseline.
2. Per-category gap analysis (task020 gap_analysis.py extended).
3. Promotion decision via task020 promotion gate (3-5% threshold
   per category).
4. Freeze checkpoint + lineage report (task069).

---

## 6. Open questions to resolve before kicking off

These design calls block specific tasks. Document the resolutions
in each `workspace/tasks/taskNNN_*/task_knowledge.md` as decided.

Inherited from roadmap §7:
- **task029 safety judge models**: which judge models for jailbreak /
  over-refusal? Reuse external evals or train classifier?
- **task031 cross-harness licensing**: can we reuse OpenHands /
  OpenCode / Codex trajectories or re-collect?
- **task036 shadow-eval frequency**: per-checkpoint, every-N-steps,
  or policy-lag triggered?

New for M2:
- **task022 browser harness**: Playwright direct, or via a managed
  service (Browserbase / Anthropic Computer Use API)? Affects
  sandbox isolation guarantees and cost.
- **task024 BIRD execution**: SQLite (cheap, isolated) or Postgres
  (closer to BIRD's intended target)? Choice affects sandbox
  container manifest.
- **task026 SWE harness selection**: which 2 of {OpenHands, OpenCode,
  Codex, Aider} for cross-harness training? Licensing + maintenance
  cost differ.
- **task028 long context 1M**: does the base checkpoint support
  1M context with reasonable quality? If not, defer 1M to M3 and
  cap M2 at 512K.
- **task032 rollout store backend**: object storage + SQLite index
  (cheap, on-prem) vs hosted (W&B Artifacts / S3 + dynamo)?
- **task034 judge pool calibration**: per-env or per-rollout
  calibration? Affects judge cost and reward variance.
- **task038 dynamic sampling signal**: per-env pass-rate, per-env
  gradient norm, or hybrid? Plan §7 says "env gap" — define
  "gap" precisely (vs target benchmark? vs internal baseline?).
- **M2 promotion baseline**: who freezes the Qwen3.5-122B-A10B
  benchmark numbers we measure against? Public results vary by ±2%
  across reproductions.

---

## 7. Risks vs PRD §11

| Risk | M2 mitigation |
|---|---|
| Base checkpoint insufficient for 122B parity | Flag early via M1 → M2 regression report (task020 gap_analysis.py); if 4+ categories regress, hold M2 kickoff and revisit SFT v1 / distillation. |
| Reward hacking in non-verifiable envs | task036 shadow-eval + task035 contamination check + task034 judge ensemble; one failing shadow split blocks promotion. |
| Slow env throughput collapse | task033 fast/slow queue + task037 health dashboard; per-env quota cap forces high-throughput envs to share gradient budget. |
| Sandbox instability (SWE / browser) | task050 (M3 sandbox pool) is the long-term answer; M2 stop-gap is per-env timeout + retry + failure-accounting from task017 watchdog policy. |
| Tool-call format drift | task007 (landed) keeps tool-syntax SFT replay; M2 task029 / task036 add invalid-tool gates. |
| Category regression after RL | task020 promotion gate (extended in task039 S4) + plan-level rollback rules. |
| Data leakage | task035 contamination pipeline; HF revision pins (task065) enforce snapshot stability. |
| **New M2-specific**: judge model drift | task034 versioning + calibration sets; freeze a judge version per training campaign. |
| **New M2-specific**: rollout store cost | task032 design must cap at sane retention (suggest 90 days hot, archive cold); index keys lean to avoid blow-up. |

---

## 8. Definition of "M2 done"

The M2 milestone is complete when **all** of the following are
true (per PRD §3 + §9):

1. ≥ 35 environments registered + smoke-tested across the 8
   families above.
2. Agentic SFT v1 checkpoint produced (task031 cluster run done).
3. Final M2 RL checkpoint produced via task038 + task033 quota'd
   scheduler.
4. Full M2 eval basket run (task039) produces weighted parity vs
   Qwen3.5-122B-A10B, **no category > 3-5% behind**.
5. Promotion gate (extended task020 gate) outputs PROMOTE for the
   final checkpoint.
6. Shadow-eval split (task036) passes for the promoted checkpoint.
7. Lineage report (task069) covers all M2 data + checkpoints +
   eval reports.
8. Regression report vs Super3 / M1 checkpoint shows no category
   went backwards by > 2% (no regression rule).

A frozen `m2_checkpoint` + a `regression_report.md` + a per-env
training-metrics dump are the final deliverables.

---

## 9. Appendix — workspace scaffolds

Status as of 2026-05-21 (✓ = directory exists in `workspace/tasks/`;
✗ = still missing):

```
✓ workspace/tasks/task022_m2_browser_search_s1/
✓ workspace/tasks/task023_m2_taubench_multi_domain_s1/
✓ workspace/tasks/task024_m2_sql_execution_s1/
✓ workspace/tasks/task025_m2_terminalbench_v2_s1/
✓ workspace/tasks/task026_m2_swe_multi_harness_s1/
✓ workspace/tasks/task027_m2_multilingual_if_code_s1/
✓ workspace/tasks/task028_m2_long_context_s1/
✓ workspace/tasks/task029_m2_safety_jailbreak_overrefusal_s1/
✗ workspace/tasks/task031_agentic_sft_v1/
✓ workspace/tasks/task032_rollout_store_s1/
✗ workspace/tasks/task033_env_scheduler/
✗ workspace/tasks/task034_judge_pool/
✓ workspace/tasks/task035_contamination_pipeline_s1/
✓ workspace/tasks/task036_shadow_eval_pipeline_s1/
✓ workspace/tasks/task037_env_health_dashboard_s1/
✗ workspace/tasks/task038_m2_rl_curriculum/
✗ workspace/tasks/task039_m2_eval_basket/
```

Naming convention drift: the landed scaffolds use a `_s1` suffix
(e.g. `task022_m2_browser_search_s1`) and a longer family-descriptive
name vs the shorter convention proposed in the 2026-05-20 draft of
this plan. Going forward, either convention is fine; the long-form
`taskNNN_<family>_<sN>` form makes session boundaries explicit and
matches what the parallel interns produced.

Each scaffold ships with:
- `README.md` — scope, dependencies, sessions table, acceptance
  (only `task022_m2_browser_search_s1` and `task028_m2_long_context_s1`
  have READMEs at 2026-05-21; the others are knowledge/history only)
- `task_knowledge.md` — open-questions resolutions as they land
- `history_log.md` — PR landings, blockers, decisions

---

## 10. Status snapshot (2026-05-21 — post parallel-landing sync)

Between the 2026-05-20 draft of this plan and the 2026-05-21
fast-forward sync, `intern_nem_dev_1`, `intern_nem_dev_2`, and
`intern_nem_dev_3` landed 12 PRs that move ~70% of Phase 1
sandbox work into main. Sandbox baseline 829 → 934 passed
(+105 tests, 7 skipped unchanged).

### Landed Session 1's

**Environment expansion (all 8 envs)**

| Task | PR | New env IDs | Code modules |
|---|---|---|---|
| task022 browser/search | (recorded in scaffold) | `browser_qa`, `browsecomp_grounded` | env_registry + `browser_grounded_answer_stub` verifier (offline) |
| task023 TauBench multi-domain | (recorded in scaffold) | `taubench_retail`, `taubench_telecom` | env_registry + converter scaffolding |
| task024 BIRD execution | (recorded in scaffold) | `sql_execution_mode` field on `sql_text_to_query` | `m2_sql_execution/sqlite_verifier.py` |
| task025 TerminalBench v2 | (recorded in scaffold) | `terminal_workplace` | env_registry only at S1 |
| task026 SWE multi-harness | (recorded in scaffold) | (no new env; harness adapter) | `m1_swe2/swe_multi_harness.py` |
| task027 Multilingual IF/code | (recorded in scaffold) | `multilingual_ifeval`, `multilingual_humaneval` | env_registry + tests |
| task028 Long context | PR #137 | `long_context_ruler`, `long_context_aalcr`, `long_context_doc_qa` | env_registry + new `long_context_qa` span-aware verifier in run_m0_health_baseline |
| task029 Safety/jailbreak/over-refusal | PR #136 | `safety_judge`, `jailbreak_resist`, `over_refusal` | env_registry + data_registry + converter; `safety_judge_stub` reused as judge stand-in |

**M2 infra (4 of 6)**

| Task | PR | Module | Notes |
|---|---|---|---|
| task032 rollout store | PR #135 | `rollout_store/local_store.py` | `LocalRolloutStore` + `RolloutKey` + `RolloutTrace`; JSONL backend; production W&B/lineage hookup deferred |
| task035 contamination | PR #139 | `data_registries/contamination_matrix.py` | Reuses `classify_contamination_row`; new `--eval-overlap-matrix` CLI flag; live registry smoke 14/14 clean |
| task036 shadow eval | PR #138 | `shadow_eval/pipeline.py` | `build_synthetic_shadow_plan` + `evaluate_shadow_plan` reading `LocalRolloutStore`; delegates to `evaluate_promotion_gate` |
| task037 env health dashboard | PR #140 | `m2_env_health_dashboard/dashboard.py` | Reads recorded `health_baseline_report.json`; slow-signal + telemetry-gap detection; Grafana/W&B board layout TBD |

### Still missing (Phase 1 work to do)

| Task | Reason it didn't land yet |
|---|---|
| **task031** Agentic SFT v1 | Depends on ≥ 4 of task022-028 to provide multi-turn data sources; Session 1 (supervision builder design + failure-rollout schema) is now sandbox-actionable |
| **task033** Env scheduler | Needs task032 backpressure signal (now available) + a quota policy model |
| **task034** Judge pool | Generalizes task018 GenRM router; needs at least design + interface contract; the model deployment itself is cluster-bound |
| **task038** M2 RL curriculum | Needs task032 (have it) + task034 (don't have it yet); the per-env gap estimator + dynamic sampler can land sandbox-only |
| **task039** M2 eval basket | Depends on ≥ 6 of task022-028 (have all 8) + task020 promotion gate (have it); the new benchmark adapter configs can land sandbox-only |

### Recommended next sandbox picks (after this sync)

1. **task033 Session 1** — env scheduler interface design + quota
   policy model (rides on the now-landed `LocalRolloutStore` for
   backpressure). Sandbox-runnable.
2. **task034 Session 1** — judge pool interface + versioning
   contract; mock judge for sandbox tests. Sandbox-runnable.
3. **task038 Session 1** — per-env gap estimator + dynamic-sampler
   logic against synthetic rollout traces. Sandbox-runnable.
4. **task039 Session 1** — benchmark adapter configs (HLE,
   BrowseComp, BIRD-real, BFCL-full, MCP-Mark, Tool Decathlon,
   multilingual). Sandbox-runnable.
5. **task031 Session 1** — multi-turn supervision builder design
   doc + failure-rollout schema (reads from `LocalRolloutStore`).
   Sandbox-runnable.

Plus **Session 2** for the 12 landed tasks: bridge wiring +
production hardening (still mostly sandbox; a few hooks
need real lineage / cluster access).

After these ~5 sandbox PRs land, M2 Phase 1 is fully scaffolded.
Phase 2 (cluster smoke for each landed task) becomes the next
bottleneck and is gated on the Group A predecessor closure (§1).
