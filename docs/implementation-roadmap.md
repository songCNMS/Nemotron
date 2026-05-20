# Implementation Roadmap — M1 RL → M3 Freeze

Last updated: 2026-05-19 (roadmap refinement pass — task013 Session 2
split into 2a/2b; task017 Session 2 OpenHands wrapper deferral lifted
to **task070** [renamed from task067 after ID collision with
`task067_m1_agentic_qwen_scaleup` landed on main concurrently];
task018 Session 2 tool-call pairing deferral lifted to task068;
task021 Session 7 W&B publish lifted to task069; task040 W1 difficulty
curriculum sampler scaffolded.)

Companion to `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md`
(the plan) and `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md`
(the v1 review findings). The plan describes what we want to build; the review
describes what has shipped; this document is the gap analysis between them and a
proposed task ordering to close the gaps.

Legend: ✓ implemented · ◐ partial · ✗ not started · 📋 tracked under an existing
workspace task.

## Current state snapshot (2026-05-19)

**Sandbox-runnable M1 layer**: complete across task013-021 + task030
(see §5). All M0 → M1 bridges, data converters, schema layer, audits,
eval basket data+gate+gap-analysis, sandbox container scaffolding,
and rollout-policy guard rail are landed and tested (sandbox baseline
494 passed + 7 skipped).

**Cluster-bound M1 work remaining**: see §5 "Cluster work queue" —
real launches (Ray + vLLM + NeMo-Gym), HF downloads at full scale,
GenRM judge service deployment, end-to-end RLHF smoke, W&B artifact
publishing (task069), OpenHands library integration (task070),
RLHF tool-call pairing harness (task068), task013 Session 2b cluster
verify.

**Recent learnings** (from task065 post-merge review):
- M0 data row `hf_revision: TBD` was silently passing the audit before
  task065 added `tbd` to FLOATING_REVISION_REFS — going forward, new
  M0 rows must use a real commit hash or `null` (null is caught as
  blocker; never TBD).
- SWE-Gym-Lite real shape is SWE-Bench-style (instance_id / repo /
  problem_statement / patch), NOT agent trajectories — converters now
  fall back to synthetic single-turn trajectories when `messages` is
  missing.
- HelpSteer-2 default config is scalar rating rows, not paired —
  `iter_helpsteer2_preference_pairs()` streaming adapter buffers
  adjacent same-prompt scalar rows. Never assume HF schema without
  verifying.

Earlier state: PR #18 merged structured output into `main`; task005
added terminal basics, short SWE patch supervision, and tool-call repair
negatives. task056 Session 1 (PR #25) wired NuminaMath + MuSiQue + multi-
turn Hermes. task012 shipped `super3.jinja`. REVIEW_v0.md still has 1
design-class item outside task005 (#9 two-stage SFT loss).

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
| REVIEW #9 | §5.1 two-stage SFT loss | ⚠ — Session 1 + 2a landed (math + dispatch + driver + stage-a/stage-b YAMLs); behavior under default config still byte-for-byte identical to pre-task013 (gpt_step). Cluster verify (Session 2b) pending. | **task013_super3_sft_two_stage_loss** — Session 1 ✓ (forward_step dispatch + sample-level loss math + adapter skeleton); Session 2a ✓ (`run_two_stage_finetune` driver + `stage_a_default.yaml` + `stage_b_default.yaml` + 14 sandbox tests); Session 2b cluster verify still to go |

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
- ⚠ Session 2 (sandbox part landed; cluster part deferred): bridge
  extended to emit a `combined.jsonl` (train+val concat, val rows last
  so the downstream `split_local_jsonl(val_holdout=N)` re-split is
  idempotent), `stage1_rlvr/config/data_prep/rlvr1.yaml` flipped from
  the `/lustre/.../yifuw/...` internal path to
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr1/combined.jsonl`,
  and a new `stage1_rlvr/config/smoke.yaml` (2 nodes / 8 prompts/step /
  4 train batch / max_num_steps=10 / val_at_end=true). 12 new pytests;
  sandbox baseline 409 → 421 passed. Real `nemotron super3 rl rlvr1 -c
  smoke` launch (Ray + vLLM + NeMo-Gym services) still requires cluster
  access.
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
- ⚠ Session 2 (sandbox part landed; small HF streaming smoke verified):
  `swe_pivot_tool_call` (verifier `argument_match`, max_turns=1) + new
  M0 data row `m0_swe_pivot_tool_call` pointing at
  `SWE-Gym/SWE-Gym-Lite` (apache-2.0, contamination_against [SWE-Bench
  Lite, SWE-Bench Verified]) + new converter
  `transform_swe_gym_lite_pivot` that extracts the first assistant
  tool_call when trajectories exist, or synthesizes a `view_file` pivot
  from patch-only public SWE-Gym-Lite rows. SWE1 registry's `m0_missing` row flipped
  to `active` — `SWE1_ENV_MAP` now maps `swe_pivot_tool_call →
  swe_pivot_single_step_tool_use_with_argument_comparison`. 20 new
  pytests + 2 existing today-tests flipped; sandbox baseline 421 →
  441 passed. Review follow-up pinned `hf_revision` to
  `f70b1a29ab120eb0a0ee7a1deb029825e735b2b0` and verified small real HF
  prep with an additional real-schema fallback test; full-scale prep
  remains a cluster task.
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
- ⚠ Session 2 (sandbox part landed; OpenHands wrapper deferred + HF
  download cluster-side): new M0 env `swe2_openhands_trace` (verifier
  `openhands_loop`, max_turns=200, sandbox=sif) + new converter
  `transform_swe_gym_openhands_trace` that preserves the full reference
  trajectory (unlike SWE1's first-tool-call pivot) and extracts the
  gold patch from top-level fields or trajectory `submit_patch` calls.
  SWE2 registry's `swegym` row flipped to `active` — `SWE2_ENV_MAP`
  lights up. New `m1_swe2/sandbox_watchdog.py` with `WatchdogPolicy`
  dataclass, token-prefix command_blocklist, network_policy enum, and
  subprocess enforcer (`SandboxPolicyViolation`); default policy YAML
  blocks `rm -rf /` / `sudo` / `curl` / external network. 33 new pytests
  + 2 today-tests flipped; sandbox baseline 441 → 474 passed. OpenHands
  loop wrapper deferred — without real library integration in this repo
  it's interface speculation; lifted to a follow-up session once the
  integration target is concrete.
- ☐ Session 3: Smoke launcher (1 instance, 1 generation) + in-process
  Docker fallback for developers without SLURM. Block on cluster + SIF
  images.
- ✓ Session 4: `_bridge_base.py` extracted; RLVR + SWE1 + SWE2 + RLHF
  all consume it. Shared scaffolding: JSONL/JSON helpers,
  ``discover_m0_split_files``, status vocabulary, generic
  ``load_env_registry`` (with module-specific row validator hook),
  ``derive_env_map``, ``base_coverage_report``, ``base_tag_record``,
  ``collect_mix_rows``. Per-module-specific bits stay in each
  ``prepare_m1_*_jsonl.py``: mix name, registry paths, lineage outputs,
  coverage extension fields (``sif_source_breakdown`` for SWE2,
  ``pref_dataset_breakdown`` + ``known_pref_candidates`` for RLHF).
  Net line reduction: 2121 → 1901 across the 4 prep scripts + base
  (607 lines of duplication folded down to 387 shared).
- **Acceptance:** a single SWE-Bench instance runs end-to-end with binary
  reward; logs of bash / file ops captured in rollout store.

### 1.6 M1 RLHF — GenRM alignment

`stage3_rlhf/config/default.yaml` (396 lines, KL=1e-4, GenRM router DP=8)
exists. Missing the judge service + preference data:

**task018_m1_rlhf_genrm_service** —
- ✓ Session 1: RLHF bridge skeleton (4th registry-driven bridge copy) +
  preference-data candidate registry + KL invariant pytest. New module
  `src/nemotron/recipes/super3/milestones/m1_rlhf/` with
  `rlhf_env_registry.yaml` (two NeMo-Gym envs declared:
  `genrm_compare` and `single_step_tool_use_with_argument_comparison`
  per `stage3_rlhf/config/default.yaml`),
  `rlhf_pref_data_registry.yaml` (HelpSteer-2 / UltraFeedback / Orca
  DPO pairs declared with license + revision pin requirement),
  `prepare_m1_rlhf_jsonl.py` (registry-driven; coverage block adds
  `pref_dataset_breakdown` + `known_pref_candidates`; today active=0
  → coverage-aware error). `tests/recipes/super3/test_rlhf_kl_invariants.py`
  reads `default.yaml` and asserts plan §5.6 KL trio
  (`reference_policy_kl_penalty == 1e-4`, `kl_type == "k3"`,
  `use_kl_in_reward == false`) — regression gate before any cluster run.
- ⚠ Session 2 (sandbox part landed; tool-call pairing harness deferred;
  small HF streaming smoke verified): new M0 env `helpsteer2_pref_compare` (verifier
  `genrm_compare`) + new M0 data row `m0_helpsteer2_pref` pointing at
  `nvidia/HelpSteer2` (cc-by-4.0, contamination_against [MT-Bench,
  HelpSteer1]) + new converter `transform_helpsteer2_pref` handling
  explicit/derived pair rows plus the public scalar-rating schema via
  adjacent same-prompt pairing (`helpfulness`+`coherence`+`correctness`
  derivation, with tie fallback and explicit-label precedence). RLHF pref-data
  registry's helpsteer2 row marked `m0_landed: true`. The env
  registry's `genrm_compare` row deliberately stays `blocked_external`
  — the GenRM judge service (Session 3 cluster ops) is the other
  blocker; row flips to `active` only when *both* blockers clear. 20
  20 new pytests; sandbox baseline 474 → 494 passed. Review follow-up pinned
  `hf_revision` to `990b2711a36180dd19d9c94b8627844866f8982a` and verified
  small real HF prep with an additional scalar-row pairing test. Tool-call validity pairing harness deferred to a follow-up (cross-product strategy
  needs design to avoid combinatorial blow-up).
- ☐ Session 3: GenRM judge model deployment (cluster ops — separate
  inference service running `nvidia/Qwen3-Nemotron-235B-A22B-GenRM-2603`
  at router_dp_size=8 / TP=8). Blocked external.
- ☐ Session 4: End-to-end RLHF smoke run from SWE2 checkpoint with the
  GenRM judge live; verify KL penalty applies; verify tool-call
  validity still passes per plan §5.6 note.
- **Acceptance:** single-prompt RLHF rollout returns judge reward; KL penalty
  applied; tool-call-validity check still passes per plan §5.6 note.

### 1.7 M1 Eval — promotion gates

`stage3_eval/config/default.yaml` (203 lines) exists; plan §5.7 lists eight
benchmark families spanning ~20 benchmarks. Currently no benchmark adapter is
wired to NeMo Evaluator.

**task019_m1_eval_basket_v0** — minimum-viable for Super3 parity:
- ✓ Session 1: 8-benchmark registry + new `eval_basket_registry`
  schema kind + `regression_report.py` generator + NeMo Evaluator
  config skeleton. New module
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/` ships
  `m1_eval_basket_registry.yaml` (the 8 plan §5.7 v0 rows — MMLU-Pro,
  AIME25, GPQA, LiveCodeBench, IFBench, MultiChallenge, RULER 256K,
  TauBench airline — with adapter + category + license + gate_metric)
  and `regression_report.py` (pure-stdlib `load_eval_results` /
  `diff_eval_runs` / `format_regression_report` with 5 status values
  improved/regressed/unchanged/new/dropped + tolerance edge case).
  `stage3_eval/config/m1_basket.yaml` selects the 8 adapter task
  names, inheriting executor/deployment from `default.yaml`. The new
  `eval_basket_registry` kind is registered in
  `data_registries/schema.py` and `unified_index.yaml`, which
  simultaneously closes task030 Session 3. 22 new pytest cases.
- ☐ Sessions 2-4: cluster verify (`nemotron super3 eval -c m1_basket`
  against a real SFT checkpoint), W&B regression report publish, per-
  benchmark adapter shims (each may need its own NeMo Evaluator config
  file), and the promotion gate logic that reads `regression_report.md`
  deltas to decide promote / hold.
- **Acceptance:** `nemotron super3 eval -c m1_basket` runs against an SFT
  checkpoint, produces `regression_report.md`.

**task020_m1_eval_full_basket** — add the rest:
- HMMT, HLE, SciCode, TerminalBench, SWE-Bench Verified, AA-LCR, MMLU-ProX,
  WMT24++, BFCL, MCP-Mark, Tool Decathlon.
- Promotion gate logic: weighted-mean Super3 parity, no key-category
  regression > 1-2 %, rollback rule on safety / SWE / tool / IF (per plan
  §5.7 promotion gate).
- ✓ Session 1: 11-row full extension registry (`m1_eval_full_basket_registry.yaml`)
  reusing the `eval_basket_registry` schema kind, `unified_index.yaml`
  entry, and `stage3_eval/config/m1_full_basket.yaml` selecting all
  19 v0+full benchmarks. KNOWN_KINDS unchanged at 7 (no new kind needed
  — same shape as v0). 14 new pytests; sandbox baseline 357 → 371 passed.
- ✓ Session 2: promotion gate logic (`promotion_gate.py`) — three-tier
  severity (promote / hold / rollback), weighted-mean parity vs Super3
  (uniform-per-category), per-category regression threshold, and a
  rollback rule that fires on any drop in critical categories (SWE /
  tool_use_* / instruction_following / multi_turn_instruction + forward-
  compat safety_*). Default thresholds at the tight end of plan §5.7's
  "1-2%" range (2%). 21 new pytests; sandbox baseline 371 → 392 passed.
- ✓ Session 4: per-category gap analysis tooling (`gap_analysis.py`) —
  ranked category gaps (worst-first) with per-benchmark drill-down for
  below-threshold categories. Complements Session 2: gate gives binary
  go/no-go, gap analysis gives prescriptive "what to focus on next"
  ranking. Same input shape as `regression_report.py` /
  `promotion_gate.py` so the three modules form a complete analysis
  trio off one eval JSON. 17 new pytests; sandbox baseline 392 → 409
  passed.
- ☐ Session 3: cluster verify (`nemotron super3 eval -c m1_full_basket`
  against real SFT checkpoint with W&B publish + real Super3 baseline
  numbers).

### 1.8 M1 infra — required before scaling

Per plan §10 M1 infra list (everything downstream depends on this).
Sliced into four Sessions; tracker lives at
`workspace/tasks/task021_m1_infra_minimum/README.md`:

**task021_m1_infra_minimum** —
- ✓ Session 6: rollout-policy guard rail. New
  `ROLLOUT_POLICY_ORACLE` / `ROLLOUT_POLICY_ADVERSARIAL` constants +
  `recommended_container_runtime(rollout_policy) -> str | None`
  helper in `runtime_shim.py`. `run_python_unit_tests` gains a
  `rollout_policy: str = "oracle"` kwarg threaded through
  `score_record` → `score_rows` → `evaluate_policy` →
  `summarize_baselines` → CLI `--rollout-policy {oracle,adversarial}`
  (default oracle). When `rollout_policy=adversarial` AND
  `container_runtime is None`, the verifier raises ``RuntimeError``
  immediately rather than silently running untrusted candidate code
  on the host. Replaces the original "flip the default to docker"
  plan because there is no in-repo RLVR rollout caller today — the
  literal flip had no coherent target. Guard rail covers any future
  M1+ rollout that forgets the container runtime.
- ✓ Session 5: ContainerSandbox runtime shim wiring the Session 3
  images into the M0 verifier path. New
  `sandbox_containers/runtime_shim.py` ships `ContainerSandbox`
  dataclass + `build_argv` (docker / podman dialect + singularity exec
  dialect with `--containall --no-net --bind src:dst:ro`) + `run` +
  `sandbox_for_env(env_id, runtime)`. `run_python_unit_tests` gains a
  `container_runtime: str | None = None` kwarg threaded through
  `score_record` → `score_rows` → `evaluate_policy` →
  `summarize_baselines` → CLI `--container-runtime {docker,podman,singularity}`.
  Default `None` keeps existing in-process `sys.executable -I`
  behavior (regression-tested). When set, candidates run inside the
  registered sandbox image (env without a registered image →
  in-process fallback + `container_fallback=True` in diagnostics).
  15 new pytest cases monkey-patch subprocess; real container runs
  need a Docker daemon (Session 4 cluster verify or local dev).
- ✗ Session 4: verify NeMo-RL / Ray / vLLM / NeMo-Gym launch path on a
  real cluster (currently all configs are paper-only). Needs NemTron
  access; unsandbox-runnable.
- ✓ Session 3: SIF/Docker/Podman sandbox container build script for
  code-exec, Lean, terminal. New module
  `src/nemotron/recipes/super3/milestones/sandbox_containers/` ships
  three Dockerfiles (`code_exec.Dockerfile` python:3.12-slim + pytest;
  `lean.Dockerfile` debian + elan v3.1.1 + Lean 4 stable;
  `terminal.Dockerfile` alpine + bash + coreutils + findutils + grep +
  sed + gawk — all UID 1000 non-root), a declarative
  `sandbox_image_registry.yaml` pairing each `image_id` with its
  Dockerfile + target M0 envs + runtime recommendations
  (`--network=none`, `--memory=...`), `image_resolver.py`
  (`load_sandbox_image_registry` / `resolve_image_for_env(env_id)` /
  `image_tag` / `envs_covered_by_registry`), and
  `build_sandbox_containers.sh` (docker / podman / singularity runtime
  switch; reads the registry; supports `--only <id>` / `--dry-run`).
  Unified index (task030 Session 1) picks up the new
  `sandbox_image_registry` kind via a one-row addition. Actually
  building the images needs a Docker daemon and stays Session 5
  territory (or local dev workstation); ContainerSandbox runtime shim
  (wiring container execution into `python_unit_tests` verifier)
  likewise.
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
| W1 unified data registry across SFT + RL + Eval | §6 | Sessions 1-2 + 4 ⚠ — schema layer + unified index over 9 existing registry YAMLs (M0 data + M0 env + 4 bridge env + SIF + pref data + sandbox image) + cross-registry inventory walks + write-time enforcement via pre-commit hook (`scripts/validate_data_registries.py`) + **single source of truth for row shape** via runtime loader delegation into schema (`fail_fast=True` mode raises on first issue; audit `collect-all` mode unchanged). Eval basket registry still missing — plugs into the same index when task019 lands. | **task030_unified_data_registry** — Session 1 ✓ (schema + index + inventories) + Session 2 ✓ (CLI validator + pre-commit local hook) + Session 4 ✓ (module-local loader merge into schema; row-shape single source of truth); Session 3 (eval basket; blocked on task019/020) still to go |
| W1 difficulty curriculum sampler | §6 | task008 added bucket metadata; sampler not wired | **task040_w1_curriculum_sampler** — Session 1 ✓ landed 2026-05-19 (`bucket_rows` / `filter_solved` / `weighted_sample` in `m0_data_env/difficulty_sampler.py`; 23 pytest cases; sandbox baseline 520 → 543 passed). Session 2 (wire into data prep paths via `--curriculum-policy` CLI flag) sandbox-runnable next; Session 3 numeric pass-rate filter depends on task032 (M2). |
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
   NeMo-Gym env map + lineage). Session 2 sandbox part landed (bridge
   combined.jsonl + `data_prep/rlvr1.yaml` flipped off the internal
   /lustre path + `stage1_rlvr/config/smoke.yaml`); real cluster launch
   (Ray + vLLM + NeMo-Gym services) still to go.
5. **task015** — M1 RLVR full 21-env mix. Session 1 landed (declarative
   `rlvr_env_registry.yaml` for all 21 NeMo-Gym envs, registry-driven
   `MIX_PROFILES`, RLVR1 name audit + correction, rlvr2 lit up with 2
   M0-available envs); remaining sessions auto-light as task057 lands M0
   sources.
6. **task016** — M1 SWE1 pivot data. Session 1 landed (bridge skeleton +
   `swe1_env_registry.yaml`; SWE1 had no active M0 source — coverage-aware
   error path). Session 2 sandbox part landed (M0 SWE-Gym-Lite →
   `swe_pivot_tool_call` env + `transform_swe_gym_lite_pivot` converter
   + SWE1 active row); `SWE1_ENV_MAP` now lights up. Revision is pinned
   and small real HF prep is verified; full-scale prep + Session 3 (cluster smoke) still
   to go.
7. **task017** — M1 SWE2 sandbox runtime. Session 1 landed (SIF image
   mapping registry + resolver with path-injection guard; SWE2 bridge
   skeleton parallel to RLVR / SWE1). Session 2 sandbox part landed
   (M0 swe2_openhands_trace converter + sandbox_watchdog policy
   module). Session 4 landed (`_bridge_base.py` extraction). Session 3
   (cluster smoke + Docker fallback) and OpenHands loop wrapper still
   to go.
8. **task018** — M1 RLHF GenRM service. Session 1 landed (RLHF bridge
   skeleton with two-env registry + preference-data candidate registry
   + KL invariant pytest reading `default.yaml`). Session 2 sandbox
   part landed (new M0 env `helpsteer2_pref_compare` + converter
   `transform_helpsteer2_pref` handling both HelpSteer-2 flavors; RLHF
   pref-data registry's helpsteer2 row marked `m0_landed: true`; env
   registry's `genrm_compare` stays `blocked_external` pending Session
   3 judge service). Session 3 (GenRM judge model deployment) / Session
   4 (end-to-end smoke from SWE2 checkpoint) still to go.

Then in parallel:
9. **task013** — M1 two-stage SFT loss (plan §5.1 / REVIEW #9). Session 1
   landed (`step_dispatch._STEP_FUNCTIONS` registry + `sample_level_loss`
   pure-torch helper + `sample_level_step` adapter; defaults to `gpt_step`
   so existing configs unchanged). Session 2a landed (`run_two_stage_finetune`
   driver with injectable `finetune_fn` + `stage_a_default.yaml` +
   `stage_b_default.yaml`; sandbox-tested against a recording fake);
   Session 2b (cluster verify in nvcr Megatron-Bridge container) still
   to go.
10. **task019** + **task020** — M1 eval basket. task019 Session 1 landed
    (8-benchmark registry per plan §5.7 v0 + new `eval_basket_registry`
    schema kind unblocking task030 Session 3 + `regression_report.py`
    generator + `stage3_eval/config/m1_basket.yaml` NeMo Evaluator
    config). task020 Session 1 landed (11-row full extension reusing
    the same schema kind + `m1_full_basket.yaml` selecting all 19
    v0+full benchmarks). task020 Session 2 landed (`promotion_gate.py`
    — three-tier promote/hold/rollback severity, weighted-mean parity
    vs Super3, per-category regression threshold, rollback rule on
    SWE/tool/IF + forward-compat safety_*). task020 Session 4 landed
    (`gap_analysis.py` — prescriptive per-category gap ranking with
    per-benchmark drill-down; complements the gate's binary decision).
    All M1 eval basket sandbox work is now done — task019 Sessions 2-3
    (cluster verify + W&B publish + per-benchmark adapter configs) and
    task020 Session 3 (cluster verify) need real cluster + checkpoint
    access. task019 Session 4 (promotion gate logic) is satisfied by
    task020 Session 2.
11. **task030** — unified data registry. Sessions 1+2+3+4+5+6+7 landed
    (schema layer + unified index over 10 existing registries +
    inventory walks + `scripts/validate_data_registries.py` CLI with
    `--license-cascade` + `--check-revision-pins` + `--check-contamination`
    + pre-commit local hooks for all three audits + schema-shape
    validation + module-local loader merge so row shape has a single
    source of truth with `fail_fast=True`/`collect-all` modes preserving
    the runtime-vs-audit split + the full task058 license/contamination
    audit trio: share-alike cascade detection, HF revision-pin lint, and
    contamination_against semantic check + M1 eval basket registry
    kind/index unblocked by task019 Session 1). task030 fully landed.

After all M1 tasks land, M2 fanout (task022-038) becomes possible. M3 only
makes sense after M2 ships a working 122B-parity checkpoint.

---

## 5b. Cluster vs sandbox work queue (2026-05-19 refinement)

The M1 critical path has bifurcated: sandbox work is largely complete,
and cluster-bound work is queued waiting for NemTron access.

### Sandbox-runnable next picks (no cluster needed)

| Task | Session | Scope | Pickable now? |
|---|---|---|---|
| ~~**task013**~~ | ~~2a~~ | ~~Two-stage finetune driver + stage-a/stage-b YAML chain~~ — **landed 2026-05-19** | ✓ done |
| ~~**task040**~~ | ~~1~~ | ~~W1 difficulty curriculum sampler — `bucket_rows` / `filter_solved` / `weighted_sample`~~ — **landed 2026-05-19** | ✓ done |
| **task040** | 2 | Wire curriculum sampler into `prepare_m0_assets.py` / `prepare_m1_agentic_sft.py` data prep paths via opt-in `--curriculum-policy` CLI flag | ✓ |
| ~~**task070**~~ | ~~1~~ | ~~OpenHands wrapper Protocol + FakeOpenHandsLoop + watchdog wiring + per-turn telemetry~~ — **landed 2026-05-19** | ✓ done |
| **task056** | 2 | M0 tier1 expansion — formal Lean rows + verifier shim (some lean tooling sandbox-runnable; full verifier needs container) | ◐ |
| ~~**task057**~~ | ~~1~~ | ~~M0 tier2 — `multilingual_instruct` env + Aya converter + `multilingual_exact_or_contains` verifier (Unicode NFC + casefold, preserves CJK punctuation)~~ — **landed 2026-05-19**; data_registry row deferred to Session 1.5 pending Aya commit pin | ✓ done |
| **task057** | 2 | M0 tier2 — `long_context_qa_smoke` env via `THUDM/LongAlpaca-12k` | ✓ |
| **task057** | 1.5 | M0 tier2 — pin Aya commit SHA + add `m0_multilingual_aya` row to data_registry | partial (needs HF access) |
| **task070** | 2 | OpenHands library integration — `OpenHandsLoopAdapter` against upstream | partial |
| **task068** | 1 | RLHF tool-call pairing harness — design doc + reference paired-row shape | ✓ |
| ~~**task069**~~ | ~~1~~ | ~~W&B artifact lineage publisher (publisher module + dry-run + scripts/publish_lineage.py CLI)~~ — **landed 2026-05-19** | ✓ done |
| ~~**task069**~~ | ~~2~~ | ~~Wire `lineage_publisher.publish()` into every `prepare_*.py` so each bridge auto-publishes after writing manifest.json~~ — **landed 2026-05-19** | ✓ done |

### Cluster-bound queue (waiting on NemTron access)

| Task | Session | Blocker |
|---|---|---|
| task013 | 2b | CUDA + nvcr Megatron-Bridge container |
| task014 | 2 (cluster) | Ray + vLLM + NeMo-Gym services |
| task016 | 3 | NemTron cluster + SIF image + checkpoint |
| task017 | 3 | NemTron cluster + SIF image + checkpoint |
| task018 | 3 | GenRM judge service (Qwen3-Nemotron-235B-A22B-GenRM-2603, router_dp_size=8, TP=8) |
| task018 | 4 | End-to-end RLHF from SWE2 checkpoint (depends task017 Session 3 + task018 Session 3) |
| task019 | 2-3 | NeMo Evaluator cluster run + W&B publish |
| task020 | 3 | NeMo Evaluator cluster run on full 19-benchmark basket |
| task021 | 4 | NeMo-RL / Ray / vLLM / NeMo-Gym launch path on real cluster |
| task056 | 2 (cluster) | Lean verifier runtime container build |
| task070 | 2-3 | Real OpenHands library install + SIF integration + cluster smoke |
| task069 | 2-3 | Real W&B credentials + end-to-end pipeline run |

### M2/M3 task scaffolds (not yet created)

Tasks **022-029** (M2 env expansion), **031** (Agentic SFT v1), **032-037**
(M2 infra), **038-039** (M2 RL + eval), **041-046** (M3 envs),
**047-055** (M3 SFT/RL/infra/eval) are referenced in §2-§3 but have no
workspace directories yet. Create scaffolds when M1 freezes and M2
kickoff is imminent — earlier scaffolding without execution context
risks scope drift.

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
