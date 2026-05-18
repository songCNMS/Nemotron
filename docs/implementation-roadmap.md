# Implementation Roadmap — M1 RL → M3 Freeze

Last updated: 2026-05-18

Companion to `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md`
(the plan) and `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md`
(the v1 review findings). The plan describes what we want to build; the review
describes what has shipped; this document is the gap analysis between them and a
proposed task ordering to close the gaps.

Legend: ✓ implemented · ◐ partial · ✗ not started · 📋 tracked under an existing
workspace task.

State snapshot: PR #18 merged structured output into `main`; task005 added the
remaining terminal basics, short SWE patch supervision, and tool-call repair
negative slices. task056 Session 1 (PR #25) wired NuminaMath + MuSiQue + multi-
turn Hermes. task012 (this row, see §1.2) shipped `super3.jinja` and switched
the three data-prep configs to it. REVIEW_v0.md still has 1 design-class item
outside task005 (#9 two-stage SFT loss).

---

## 1. M1 — Super3-parity (plan §3, weeks 3-12)

### 1.1 Agentic SFT v0 — coverage shortfall

`prepare_m1_agentic_sft.py` converts M0's four environments into chat/tool SFT
records. Plan §8 v0 lists six capability targets. Coverage today:

| Capability (plan §8) | Status | Gap | Notes |
|---|---|---|---|
| tool call syntax | ✓ | — | `general_tool_calling` env, Hermes singleturn |
| search pattern | ✓ | — | `search_grounded_qa`, grounded template added in PR #13 |
| structured output | ◐ | env, converter, M1 SFT builder landed for Hermes `json_mode_singleturn`; scale data not regenerated in repo | same license/revision as the tool-calling source |
| terminal basics | ◐ | env, converter, M1 SFT builder, and lightweight verifier landed; scale data not regenerated in repo | source: `aelhalili/bash-commands-dataset`, license `mit` |
| short SWE traces | ◐ | env, converter, M1 SFT builder, and patch verifier landed; no sandbox at SFT stage | source: `princeton-nlp/SWE-bench_Lite`, license follows source repos |
| malformed tool / hallucinated tool output negatives | ◐ | synthetic repair-negative path landed from Hermes singleturn; scale data not regenerated in repo | tags `metadata.negative_kind` + `metadata.repair_target` for downstream RL repair |

The reasoning + code envs are also implemented (`math_reasoning_numeric`,
`code_execution_python`) — those aren't called out as v0 capabilities but they
are landed.

Tracked under **task005_m1_sft_v0_scope_expansion** (workspace dir exists,
status `InProgress`).

### 1.2 Agentic SFT v0 — design-class still-open

| # | Plan ref | Status | Suggested task |
|---|---|---|---|
| REVIEW #8 | §5.1 chat template | ✓ — task012 shipped `src/nemotron/data_prep/templates/super3.jinja` (verbatim copy of nano3 with a header comment for lineage), taught `_apply_chat_template` to resolve `super3`, and flipped the three data-prep YAMLs in `stage1_sft/config/data_prep/{default,agentic_v0,tiny}.yaml`. Render-time tests cover `system / user / assistant w/ tool_calls / tool turn` plus `tool_call_repair_negative` round-trip. Diverge `super3.jinja` from `nano3.jinja` as Super3-specific behavior is identified. |
| REVIEW #9 | §5.1 two-stage SFT loss | ✗ — only token-level next-token loss; plan calls for "先 token-level，再 sample-level" | **task013_super3_sft_two_stage_loss** — wire a second optimizer pass; needs Megatron-Bridge hook research first |

### 1.3 M1 RLVR 1/2/3 — data wiring (highest leverage)

`stage2_rl/stage1_rlvr/config/default.yaml` is 538 lines of production GRPO
config; `stage2_rl/data_prep.py` is 16 KB. The rlvr1/2/3 data-prep YAMLs are
27-line stubs that point at `/lustre/fs1/portfolios/coreai/projects/coreai_dlalgo_nemorl/users/yifuw/...` — an external NVIDIA path with no M0/M1 connection. We
cannot launch a verifiable smoke run from M0 assets today.

**task014_m1_rlvr_data_bridge** — bridge M0 → RLVR1 smoke:
- ✓ Session 1: New `prepare_m1_rlvr_jsonl.py` (parallel to
  `prepare_m1_agentic_sft.py`) tags M0 rows with the matching NeMo-Gym env
  name without touching the `responses_create_params` / `reward_config`
  payload that M0 already emits. M0 → RLVR1 env map:
  `math_reasoning_numeric → math_with_judge` (gsm8k),
  `code_execution_python → code_gen` (mbpp),
  `search_grounded_qa → search_grounded_qa` (hotpot),
  `general_tool_calling → general_tool_calling` (hermes). Outputs
  `train.jsonl` / `val.jsonl` / `manifest.json` consumable by the existing
  `SplitJsonlDataArtifact` shape; lineage block emits `RLVR1` artifact with
  the M0 manifest as the upstream `manifest` input.
- ☐ Session 2: Smoke launcher — `nemotron super3 rl rlvr1 -c smoke` with
  `nodes=1, gpus_per_node=1, prompts_per_step=1, max_generations=2`; flip
  `stage1_rlvr/config/data_prep/rlvr1.yaml` from the `/lustre/...` placeholder
  to the M0-derived artifact.
- **Acceptance:** end-to-end smoke run completes; reward telemetry emitted per
  env; W&B lineage `M0 → SFT artifact → RLVR1 artifact` lit up.

**task015_m1_rlvr_full_mix** — extend mix from 4 → 21 envs per plan §5.3:
- ✓ Session 1: registry-driven mix derivation. New
  `src/nemotron/recipes/super3/milestones/m1_rlvr/rlvr_env_registry.yaml`
  declares all 21 NeMo-Gym envs from `stage1_rlvr/config/default.yaml`,
  pairs each with an M0 source (or `m0_missing` / `verifier_mismatch` /
  `blocked_external`), and assigns a mix (rlvr1 / rlvr2 / rlvr3).
  `prepare_m1_rlvr_jsonl.py::MIX_PROFILES` is now derived from the
  registry; flipping a row from `m0_missing` to `active` lights up that
  env without Python edits. **Correction shipped:** task014 Session 1's
  `RLVR1_ENV_MAP` named two NeMo-Gym envs (`search_grounded_qa`,
  `general_tool_calling`) that don't appear in `default.yaml`;
  Session 1 renames `general_tool_calling` →
  `single_step_tool_use_with_argument_comparison` (verifier semantics
  match) and removes `search_grounded_qa` from active rlvr1 until a
  proper single-hop QA NeMo-Gym env exists. RLVR2 picks up two active
  envs from M0 today (math_competition_numeric, structured_outputs_json);
  RLVR3 stays empty until task057 / task016 / task056 Session 2 land.
- ☐ Session 2+: per-env M0 expansion (largely task057 territory); the
  bridge auto-picks them up as registry rows flip to `active`. Acceptance
  threshold (≥ 8 active envs across mixes) needs task057 progress.
- HF-resolution path remaining for: `workplace_assistant`, `mcqa`,
  `instruction_following`, `calendar`, `reasoning_gym`, `terminal_pivot`,
  `ns_tools`, `math_formal_lean`, `jailbreak_detection`,
  `over_refusal_detection`, `multichallenge`, `inverse_if`,
  `search_pivot_single_step_tool_use_with_argument_comparison`. Each
  needs license audit + `hf_revision` pin (task057) + NeMo-Gym verifier
  registration (external).
- **Acceptance:** rlvr1/2/3 each have a registry ✓; single-node smoke runs
  with ≥ 8 envs live ☐; per-env reward histograms in W&B ☐.

### 1.4 M1 SWE1 — pivot data

`stage2_swe1/config/default.yaml` (344 lines, prompts/step=64, gens/prompt=16,
seq_len=131K) exists. Missing the data + smoke entry:

**task016_m1_swe1_pivot_data** —
- ✓ Session 1: SWE1 bridge skeleton, mirrors task014 task015 pattern. New
  module `src/nemotron/recipes/super3/milestones/m1_swe1/` with
  `swe1_env_registry.yaml` (single NeMo-Gym target —
  `swe_pivot_single_step_tool_use_with_argument_comparison` — declared
  with two rows: one `m0_missing` slot reserved for the future M0
  source, one `verifier_mismatch` row tracking the existing M0
  `swe_pivot_patch_supervision` which uses `patch_diff_match` semantics
  rather than argument-match) and `prepare_m1_swe1_jsonl.py`. Bridge
  emits `train.jsonl` / `val.jsonl` / `manifest.json` with `coverage`
  block + `SWE1_ARTIFACT` lineage pointing at the M0 manifest. Calling
  `prepare()` today raises a coverage-aware error listing the gaps; once
  Session 2 lands an active M0 SWE pivot env, no Python edits are needed
  — the bridge auto-picks up via the registry flip. 13 new pytest cases.
- ☐ Session 2: M0 SWE pivot data converter. Source: SWE-Gym-Lite or
  R2E-Gym subsets per plan §5.4. Converter extracts the "first gold tool
  call" decision point from agent trajectories and emits rows shaped for
  the `argument_match` verifier. Lands an M0 env + registry entry; flips
  the swe1 registry row to `active`.
- ☐ Session 3: Smoke launcher (1-node, 1 prompt/step). Block on cluster
  verify (parallel to task014 Session 2).
- **Acceptance:** reward-shape verifier returns numeric reward on smoke
  rollouts; per-prompt latency p50/p99 captured.

### 1.5 M1 SWE2 — full OpenHands loop

`stage2_swe2/config/default.yaml` (368 lines, agent_max_turns=200) exists.
Missing the runtime stack:

**task017_m1_swe2_sandbox_runtime** —
- ✓ Session 1: SIF image mapping registry + SWE2 bridge skeleton. New
  module `src/nemotron/recipes/super3/milestones/m1_swe2/` with
  `swe2_sif_registry.yaml` (declarative table for the three SIF families
  per `stage2_swe2/config/default.yaml::container_formatter` — swebench /
  swegym / r2egym), `resolve_sif_path()` + `validate_sif_exists()` Python
  helpers (with `instance_id` path-injection guard), `swe2_env_registry.yaml`
  + `prepare_m1_swe2_jsonl.py` (third copy of the registry-driven bridge
  pattern). Today active=0 → `prepare()` raises a coverage-aware error;
  Session 2 lands an M0 SWE2 source and flips a registry row to active.
  Manifest coverage block extended with `sif_source_breakdown` so coverage
  explains which container family still needs an M0 source.
- ☐ Session 2: OpenHands loop wrapper (agent_max_turns runner) + M0 SWE2
  trace data converter (SWE-Gym-Lite primary candidate, multi-turn agent
  rollout shape) + sandbox health-check / memory watchdog / command
  blocklist enforcement.
- ☐ Session 3: Smoke launcher (1 instance, 1 generation) + in-process
  Docker fallback for developers without SLURM. Block on cluster + SIF
  images.
- ☐ Session 4: `_bridge_base.py` extraction now that RLVR + SWE1 + SWE2
  all use the same registry-driven bridge pattern (~80% code overlap).
- **Acceptance:** a single SWE-Bench instance runs end-to-end with binary
  reward; logs of bash / file ops captured in rollout store.

### 1.6 M1 RLHF — GenRM alignment

`stage3_rlhf/config/default.yaml` (396 lines, KL=1e-4, GenRM router DP=8)
exists. Missing the judge service + preference data:

**task018_m1_rlhf_genrm_service** —
- GenRM router deployment for `genrm_compare` env (plan §5.6) — separate
  inference service, configurable model.
- Preference data: HelpSteer-2, UltraFeedback, or similar; license + revision
  pin in the M1 registry.
- KL penalty 1e-4 path verified end-to-end (reference policy = SWE2
  checkpoint).
- **Acceptance:** single-prompt RLHF rollout returns judge reward; KL penalty
  applied; tool-call-validity check still passes per plan §5.6 note.

### 1.7 M1 Eval — promotion gates

`stage3_eval/config/default.yaml` (203 lines) exists; plan §5.7 lists eight
benchmark families spanning ~20 benchmarks. Currently no benchmark adapter is
wired to NeMo Evaluator.

**task019_m1_eval_basket_v0** — minimum-viable for Super3 parity:
- NeMo Evaluator launcher wiring.
- Adapters for MMLU-Pro, AIME25, GPQA, LiveCodeBench, IFBench,
  MultiChallenge, RULER 256K, TauBench airline.
- W&B regression report (gain/loss per task vs previous checkpoint).
- **Acceptance:** `nemotron super3 eval -c m1_basket` runs against an SFT
  checkpoint, produces `regression_report.md`.

**task020_m1_eval_full_basket** — add the rest:
- HMMT, HLE, SciCode, TerminalBench, SWE-Bench Verified, AA-LCR, MMLU-ProX,
  WMT24++, BFCL, MCP-Mark, Tool Decathlon.
- Promotion gate logic: weighted-mean Super3 parity, no key-category
  regression > 1-2 %, rollback rule on safety / SWE / tool / IF (per plan
  §5.7 promotion gate).

### 1.8 M1 infra — required before scaling

Per plan §10 M1 infra list (everything downstream depends on this).
Sliced into four Sessions; tracker lives at
`workspace/tasks/task021_m1_infra_minimum/README.md`:

**task021_m1_infra_minimum** —
- ✗ Session 4: verify NeMo-RL / Ray / vLLM / NeMo-Gym launch path on a
  real cluster (currently all configs are paper-only). Needs NemTron
  access; unsandbox-runnable.
- ✗ Session 3: SIF/Docker/Podman sandbox container build script for
  code-exec, Lean, terminal.
- ✓ Session 2: cross-stage lineage schema +
  `manifest["lineage"]` block emitted by `prepare_m0_assets.py` (root
  with HF source inputs) and `prepare_m1_agentic_sft.py` (declares the
  M0 manifest as its upstream input). New
  `src/nemotron/recipes/super3/milestones/lineage.py` ships
  `LineageRecord` / `LineageInput` / `LineageOutput` dataclasses +
  `walk_chain` / `validate_chain` walkers. Plan §10 artifact-type
  vocabulary (`RawDataArtifact → SFTDataArtifact → ModelArtifact-sft →
  RLVR{1,2,3} → SWE{1,2} → RLHF → EvalReport`) is enumerated as
  module constants so the future W&B publish wiring (Session 3+)
  inherits the type names. Sandbox-runnable; W&B publish still needs
  runtime credentials.
- ✓ Session 1: per-env telemetry emitter for the M0 oracle health-
  baseline path. `run_m0_health_baseline.py` now threads each scorer
  through a `time.perf_counter()` wrap and emits per-verifier
  telemetry (`latency_ms` everywhere; `invalid_tool_call` /
  `argument_match` / `malformed_final_answer` / `timeout` /
  `runtime_error` / `command_match` / `patch_match` / `repair_target_match`
  per verifier). `summarize_baselines` cross-checks
  env_registry's declared `telemetry: [...]` list against what scorers
  actually emit and surfaces the diff as `telemetry_gap` so the
  registry stops "lying". Aggregate block summarizes per-row values
  (numeric → min/mean/max, bool → true/false counts, other → distinct).
  Sandbox-runnable; the shape is the contract that the future
  stage2_rl runtime emitter (Session 2+) plugs into without schema
  changes.

---

## 2. M2 — Qwen3.5-122B-A10B parity (plan §3, weeks 13-23)

Status: entirely missing.

### 2.1 Environment expansion (35-50 envs)

| Family | Plan ref | Current | Gap |
|---|---|---|---|
| browser / search | §7 | ✗ | env, Playwright sandbox, data converter |
| TauBench multi-domain | §7 | airline (M1 planned) | retail, telecom |
| BIRD / text-to-SQL | §7 | ✗ | DB sandbox, schema fixtures, SQL execution verifier |
| TerminalBench v2 | §7 | ✗ | upgraded harness, longer task budgets |
| SWE multi-harness | §7 | OpenHands (M1 planned) | OpenCode, Codex agent classes |
| Multi-lingual IF / code | §7 | ✗ | translation + 多语言 task corpora |
| Long context | §7 | RULER 256K (M1 planned) | RULER 512K / 1M, AA-LCR, long-doc QA |
| Safety / jailbreak / over-refusal | §7 | ✗ | judge models, calibration sets |

One task per family: **task022** browser/search, **task023** TauBench, **task024** BIRD, **task025** TerminalBench v2, **task026** SWE multi-harness, **task027** multilingual, **task028** long-context, **task029** safety. Each ~1-2 weeks; all depend on **task021**.

### 2.2 Agentic SFT v1

Plan §8 v1 scope:
- Multi-turn tool traces with observation handling.
- Self-correction trajectories.
- Failure-repair trajectories.
- Cross-harness SWE traces (OpenHands + OpenCode + Codex).
- Compact / low-effort reasoning variants.

→ **task031_agentic_sft_v1** — depends on ≥ 4 of task022-028 (need multi-turn
data sources). Also folds in the **W1** failure-rollout-to-SFT-repair pipeline.

### 2.3 M2 RL infrastructure

Per plan §10 M2 infra:

| Component | Status | Suggested task |
|---|---|---|
| Central rollout store | ✗ | **task032_rollout_store** — schema, write path, indexed retrieval keyed on `(prompt_id, model_version, env_id)` |
| Env scheduler (quota, backpressure, fast/slow queue split) | ✗ | **task033_env_scheduler** — depends on task032 for backpressure signal |
| Judge service pool (model versioning + calibration) | ✗ | **task034_judge_pool** — generalizes the GenRM router from task018 |
| Contamination check + eval-overlap report | ✗ | **task035_contamination_pipeline** — reuses task001's `contamination` metadata field |
| Canary + shadow-eval pipeline | ✗ | **task036_shadow_eval** — uses task019/019 harness with held-out splits |
| Env health dashboard | ✗ | **task037_env_health_dashboard** — Grafana/W&B board over telemetry stream |

### 2.4 M2 RL recipe — curriculum & dynamic sampling

Plan §9 M2:
- Per-environment quota.
- Dynamic sampling by env gap.
- Judge ensemble for non-binary rewards.
- Per-environment reward calibration.

→ **task038_m2_rl_curriculum** — depends on task032 (rollout store) + task034
(judge pool).

### 2.5 M2 eval expansion

Add to task020 basket:
- HLE, BrowseComp, BIRD, BFCL (full), MCP-Mark, Tool Decathlon.
- Multilingual IF / code / tool.
- Per-category gap analysis: weighted parity, single-task gap ≤ 3-5 %.

→ **task039_m2_eval_basket**.

---

## 3. M3 — Qwen3.5-397B-A17B parity (plan §3, weeks 24-33)

Status: entirely missing.

### 3.1 Environment expansion to 70-100+

Per plan §11:
- GUI / MCP / browser (Playwright + MCP servers).
- Deep SWE (multi-repo, harder benchmarks).
- Code safety.
- Long-horizon workplace assistant.
- Multilingual agent.
- RULER 1M+ long-context.
- Stronger safety / alignment.

→ **task041–task046**, one per family.

### 3.2 Agentic SFT v2

Plan §8 v2 + plan §9 M3:
- Distill M2 high-reward rollouts (depends on rollout store from task032).
- Hard-negative repair trajectories.
- Teacher reranking.
- GenRM reranking.

→ **task047_agentic_sft_v2** — depends on task031 + task032 + task034.

### 3.3 M3 RL — three-wave training

Plan §9 / §11:
- Wave 1: high-confidence RLVR.
- Wave 2: slow agentic (SWE / browser / GUI).
- Wave 3: final GenRM / RLHF with KL.

→ **task048_m3_rl_waves** — depends on full M2 stack.

### 3.4 M3 infra — 1K-GPU class

Per plan §10 M3 infra:

| Component | Suggested task |
|---|---|
| 1K-GPU async GRPO with policy-lag monitoring + auto recovery | **task049_async_grpo_1k** |
| Sandbox pool manager (resource / timeout / fs isolation, artifact capture) | **task050_sandbox_pool** |
| Env replay / debug UI | **task051_replay_ui** |
| Checkpoint promotion / rollback gates | **task052_promotion_gates** |
| BF16 + quantization serving validation | **task053_serving_validation** |
| Final checkpoint freeze (week 33) | **task054_checkpoint_freeze** |

### 3.5 M3 eval freeze

→ **task055_m3_eval_basket_freeze** — `BFCL, TAU2, VITA, DeepPlanning, Tool
Decathlon, MCP-Mark, SWE-Bench, TerminalBench, HLE, GPQA, LiveCodeBench,
long-context, multilingual` per plan §3 M3 acceptance.

---

## 4. Cross-cutting work

| Workflow | Plan ref | Gap | Suggested task |
|---|---|---|---|
| W1 unified data registry across SFT + RL + Eval | §6 | M0 has registry; M1 SFT links to M0; RL and eval data have no registry | **task030_unified_data_registry** — merge M0 yaml format, extend with RL/eval fields |
| W1 difficulty curriculum sampler | §6 | task008 added bucket metadata; sampler not wired | **task040_curriculum_sampler** — depends on task008 (bucket metadata) + task032 (rollout store) |
| W1 failure rollout → SFT repair pipeline | §6 | ✗ | folded into task031 / task047 |
| W2 env telemetry emitter | §7 | env_registry lists names; emitter missing | folded into task021 + task037 |
| W2 per-env held-out shadow split | §7 | ✗ | folded into task036 |

---

## 5. Recommended ordering — next 8 PRs

Critical path to the M1 promotion gate, single-track execution:

1. **task005** *(landed)* — Agentic SFT v0 scope expansion (terminal /
   structured / short SWE / negatives).
2. ~~**task012** — Super3 chat template~~ *(landed; REVIEW #8 closed)*.
3. **task021** — M1 infra minimum (lineage + telemetry; everything downstream
   depends on this). Sessions 1-2 landed (telemetry emitter + cross-stage
   lineage schema/wiring); Session 3 (sandbox containers) + Session 4
   (cluster verify) still to go.
4. **task014** — M1 RLVR data bridge (smoke-run-able from M0 in one day).
   Session 1 landed (M0 → RLVR1 JSONL bridge `prepare_m1_rlvr_jsonl.py` +
   NeMo-Gym env map + lineage); Session 2 (RLVR1 config wiring + smoke
   launcher) still to go.
5. **task015** — M1 RLVR full 21-env mix. Session 1 landed (declarative
   `rlvr_env_registry.yaml` for all 21 NeMo-Gym envs, registry-driven
   `MIX_PROFILES`, RLVR1 name audit + correction, rlvr2 lit up with 2
   M0-available envs); remaining sessions auto-light as task057 lands M0
   sources.
6. **task016** — M1 SWE1 pivot data. Session 1 landed (bridge skeleton +
   `swe1_env_registry.yaml`; SWE1 currently has no active M0 source —
   coverage-aware error path); Session 2 (M0 SWE pivot converter from
   SWE-Gym-Lite / R2E-Gym) + Session 3 (cluster smoke) still to go.
7. **task017** — M1 SWE2 sandbox runtime. Session 1 landed (SIF image
   mapping registry + resolver with path-injection guard; SWE2 bridge
   skeleton parallel to RLVR / SWE1; coverage-aware error today); Session
   2 (OpenHands loop wrapper + M0 SWE2 trace converter + sandbox watchdog)
   / Session 3 (cluster smoke + Docker fallback) / Session 4
   (`_bridge_base.py` extraction) still to go.
8. **task018** — M1 RLHF GenRM service.

Then in parallel:
9. **task019** + **task020** — M1 eval basket (can start once task014 has a
   real checkpoint).
10. **task030** — unified data registry (saves cleanup work across M2).

After all M1 tasks land, M2 fanout (task022-038) becomes possible. M3 only
makes sense after M2 ships a working 122B-parity checkpoint.

---

## 6. Risks vs plan §12

| Risk | Mitigation hook in this plan |
|---|---|
| Base checkpoint capability insufficient | task018 RLHF + task013 two-stage loss may not be enough; flag early in task014 smoke run if reward variance is low |
| Reward hacking | task036 shadow-eval + task035 contamination check + task034 judge ensemble |
| Slow env throughput collapse | task033 fast/slow queue + task037 health dashboard |
| Sandbox instability | task050 sandbox pool with memory watchdog + retries |
| Tool-call format drift | REVIEW #14 (task007, landed) + chat template work (task012) |
| Category regression after RL | task052 promotion gate + plan-level rollback rule |
| Data leakage | task035 contamination pipeline |

---

## 7. Open questions to resolve before kicking off

These are the design calls that can't be made without product / lead input:

- ~~**task012 chat template:** does Super3 ship its own jinja template, or do
  we formalize that Super3 reuses Nano3?~~ — resolved by task012: ships its
  own (`super3.jinja`); starts as a verbatim copy of `nano3.jinja` and may
  diverge as Super3-specific behavior surfaces.
- **task014 RLVR base checkpoint:** are we starting from `super3-sft` artifact
  produced by the existing super3 SFT recipe, or from the new M1 Agentic SFT
  v0 checkpoint? Plan §5 implies the latter — confirm.
- **task018 GenRM model:** which model do we use for `genrm_compare`?
  Plan §10 mentions "GenRM router DP size 8" — implies a sizable judge model.
- **task029 safety:** which judge models for jailbreak / over-refusal? Will we
  reuse Anthropic / OpenAI evals, or train our own classifier?
- **task031 SFT v1 cross-harness:** OpenHands / OpenCode / Codex licensing —
  can we reuse their trajectories or do we need to re-collect?
- **task036 shadow-eval frequency:** every promotion, every N steps, or
  policy-lag-triggered? Plan §5.7 says "每个 promoted checkpoint" — once per
  checkpoint sufficient?

Resolving these unblocks the corresponding tasks. Document the answers in the
matching `workspace/tasks/taskNNN_*/task_knowledge.md` once decided.
