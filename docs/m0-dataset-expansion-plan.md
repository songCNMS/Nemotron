# M0 Data Foundation — Expansion Plan

Last updated: 2026-05-17

Companion to `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md`
(plan §3, §6, §7) and `docs/implementation-roadmap.md`. Scopes the M0 work
needed to give M1+ a real data foundation, not just the four smoke envs we
ship today.

## 1. State as of `main` (post-task011)

Four M0 environments are end-to-end wired (data registry, environment
registry, NeMo-Gym JSONL contract, oracle health gate, difficulty signal):

| Env | Source | Plan §7 family |
|---|---|---|
| `search_grounded_qa` | `hotpotqa/hotpot_qa` distractor | Search / Browser |
| `code_execution_python` | `google-research-datasets/mbpp` full | Code Generation |
| `general_tool_calling` | `NousResearch/hermes-function-calling-v1` singleturn | Tool Use |
| `math_reasoning_numeric` | `openai/gsm8k` main | Math / Reasoning |

That covers ~40 % of plan §7's ten family list and ~25 % of the production
Super3 SFT blend's category list (`stage1_sft/config/data_prep/data_blend_raw.json`
documents twelve "missing categories" with weights against the internal
7M-sample blend). The four envs are sufficient as smoke targets but not as a
foundation for M1 RLVR (plan §5.3 cites 17+ envs) or M1 SFT v0 (plan §8 names
six v0 capabilities, four still uncovered).

## 2. Production references uncovered during the audit

Beyond plan §7, the production stack on `main` references additional public
HF datasets:

- `nvidia/Nemotron-Instruction-Following-Chat-v1` — subsets `chat_if`,
  `structured_outputs` (ODC-BY-1.0 / CC-BY-4.0; 431 K rows).
- `nvidia/Nemotron-Competitive-Programming-v1` — cpp / python / infinibyte
  (CC-BY-4.0; 3.9 M rows). Repo subset names use `_part00` not `.part_00` —
  data_blend_raw.json reference will fail to load until the dot vs underscore
  mismatch is fixed.
- `nvidia/Nemotron-SWE-v1` — `r2e_gym` (CC-BY-4.0; 51 K). Possible overlap
  with SWE-Bench Verified instances; needs filter before SWE eval.
- `nvidia/Nemotron-Math-Proofs-v1` — Lean split (CC-BY-SA-4.0 ⚠;
  share-alike obligations cascade through derived artifacts; ~925 K).
- `nvidia/Nemotron-Agentic-v1` — `interactive_agent` (19 K) + `tool_calling`
  (316 K). CC-BY-4.0 + Apache-2.0.
- `nvidia/Nemotron-RL-Super-Training-Blends` — RLVR1 (139 K) / RLVR2 (156 K) /
  RLVR3 (107 K) / SWE1 (51 K) / SWE2 (1.4 K) / RLHF (25 K). **The current
  code refers to `Nemotron-3-Super-RL-Training-Blends` (with a `-3-`) — this
  slug 404s; the live repo dropped the `-3-`.** Tracked by task058.
- `BytedTsinghua-SIA/DAPO-Math-17k` (Apache-2.0; 1.79 M). **No benchmark
  scrub documented** — any M1 RLVR using it should add a MATH / AIME / GSM8K
  decontamination pass.
- `Skywork/Skywork-OR1-RL-Data` math + code splits (license unstated on the
  card; flag for legal review). Decontaminated vs AIME-24/25 and
  LiveCodeBench by upstream.

## 3. Gap analysis, prioritized

Priority criteria:
- (a) blocks a downstream M1 RL stage with no clean workaround
- (b) explicitly named in plan §7 as one of the ten families
- (c) has a clean public dataset with a permissive license

### Tier 1 — high priority, clean fits (target: task056)

| Env id (M0) | HF source | License | Rows | Verifier | Wired in this PR |
|---|---|---|---|---|---|
| `math_competition_numeric` | `AI-MO/NuminaMath-CoT` | Apache-2.0 | 859 608 | `normalized_exact_or_contains` (matches the `\boxed{…}` answer span) | ✓ |
| `search_multihop_qa` | `dgslibisey/MuSiQue` (Ans) | CC-BY-4.0 | 24 814 | `normalized_exact_or_contains` (mirrors HotpotQA verifier) | ✓ |
| `multi_turn_tool_use` | `NousResearch/hermes-function-calling-v1` (`func_calling` config) | Apache-2.0 | reuses existing pin | `tool_schema_and_argument_match` + trajectory check | ✓ |
| `structured_outputs_json` | `nvidia/Nemotron-Instruction-Following-Chat-v1` (`structured_outputs`) | CC-BY-4.0 | 4 969 | new `json_structured_output_match` stub | ✗ — see task056 |
| `math_formal_lean` | `nvidia/Nemotron-Math-Proofs-v1` (Lean split) | CC-BY-SA-4.0 ⚠ | ~925 K | new `lean_proof_stub` verifier (M0 stage only checks non-empty) | ✗ — see task056 |
| `swe_pivot_patch_supervision` | `nvidia/Nemotron-SWE-v1` (`r2e_gym`) | CC-BY-4.0 | 51 029 | new `patch_diff_stub` verifier | ✗ — see task056 |
| `tool_call_repair_negative` | synth from `func_calling_singleturn` | Apache-2.0 | ≤ 100 / env | new `negative_recognition` verifier | ✗ — see task056 / task005 |

This PR wires the first three; the remaining four are scoped under task056
and depend on slightly more code (new verifier registration or synthesis
pipeline).

### Tier 2 — plan-§7 mandated, but each has a notable contamination or licensing concern (task057)

| Env id (M0) | HF source | License | Concern |
|---|---|---|---|
| `sql_text_to_query` | `birdsql/bird_mini_dev` (3 dialects) + `bird-bench/bird` train | CC-BY-SA-4.0 ⚠ | `mini_dev` is the BIRD eval slice — keep held out |
| `terminal_basic_shell` | candidate `CLI-1M` (Apache-2.0) or `epinnock/intercode-nl2bash-curated` (CC-BY-4.0) | Apache / CC-BY | CLI-1M was forum-announced, verify exact HF path |
| `safety_reasoning_smoke` | `nvidia/Nemotron-Content-Safety-Reasoning-Dataset` | CC-BY-4.0 | Viewer schema issues — loader validation needed |
| `multilingual_instruct` | `CohereLabs/aya_dataset` (204 K human-written) | Apache-2.0 | Bigger Aya Collection has translated FLAN; prefer the human-written subset for smoke |
| `long_context_qa_smoke` | `THUDM/LongAlpaca-12k` train, reserve `zai-org/LongBench-v2` for eval | Apache-2.0 | LongBench-v2 is eval-only |
| `math_with_tools` | `MathLLMs/MathCodeInstruct` or `nvidia/OpenMathInstruct-2` | Apache-2.0 / CC-BY-4.0 | Both built on GSM8K/MATH seeds — heavy contamination, audit before eval |

### Tier 3 — defer past M0 smoke

- Science STEM (12.8 % of production blend) — not on plan §7's family list.
- Financial / SEC reasoning (3.0 %) — not on plan §7.
- CUDA kernel (0.5 %) — niche; M1+ at earliest.
- Low-effort-reasoning mode (2.0 %) — no clean canonical fit; revisit after
  task012 chat-template work decides reasoning-mode markers.
- Agentic programming Codex/OpenCode-style — best public corpus
  `AlienKevin/SWE-ZERO-12M-trajectories` is SWE-bench-contaminated; this
  belongs in M1 SWE1 (task016) and M2 SFT v1 (task031) with a filtering
  pipeline.

## 4. Production bugs uncovered while doing this audit

Tracked under task058 (separate small fix PR):

1. **HF slug fix:** `stage2_rl/data_prep.py` and `_data_prep_base.py` point at
   `nvidia/Nemotron-3-Super-RL-Training-Blends`. The live repo is
   `nvidia/Nemotron-RL-Super-Training-Blends`. Current path 404s.
2. **Subset naming:** `stage1_sft/config/data_prep/data_blend_raw.json` uses
   `competitive_coding_cpp.part_00` (dot); the HF repo uses `_part00`
   (underscore, no dot). Loader will fail.
3. **Skywork-OR1-RL-Data missing license** on the HF card — flag for legal
   review before any commercial RL run.
4. **DAPO-Math-17k contamination:** no benchmark scrub documented. Add
   `contamination` metadata + an explicit decontamination pass before any
   M1 RLVR launches against MATH / AIME / GSM8K eval.

## 5. Wiring rules — what counts as "wired" at M0

For each new env, the same six-point checklist (matching the existing four
envs):

1. `data_registry.yaml` entry with `hf_dataset`, `hf_config`, `hf_revision`,
   `hf_split`, optional `hf_val_split`, `license`, `domain`, `reward_type`,
   `contamination`, `use_stage`.
2. `environment_registry.yaml` entry with reward verifier, range, semantics,
   resource budget, telemetry list, health-check `min_rows_per_split` and
   `required_fields`.
3. Converter function in `prepare_m0_assets.py` that produces a NeMo-Gym
   record matching the M0 JSONL contract; registered in `CONVERTERS`.
4. System prompt entry in `SYSTEM_PROMPTS` if the env needs a non-shared
   prompt.
5. Verifier registration in `run_m0_health_baseline.py` (or proof that an
   existing verifier suffices).
6. M1 SFT supervision builder (`assistant_for_*` or the tool-trajectory path)
   in `prepare_m1_agentic_sft.py` so the M1 entry can consume the new env;
   plus an entry in `M1_USE_BY_ENV` so the metadata reflects the actual skill
   the row exercises.

This PR demonstrates the pattern with three envs; the remaining tier-1 and
tier-2 envs follow the same shape.

## 6. Open questions to resolve before tier-2 / tier-3 work

1. **Share-alike posture:** are CC-BY-SA-4.0 sources (Nemotron Lean proofs,
   BIRD SQL) acceptable? Share-alike obligations cascade through any derived
   artifact (eval reports, distilled SFT data).
2. **Contamination policy:** every M0 source used in M1+ eval must be
   deduped against M0 train + val. Recommend adding a `contamination_against`
   field on each spec; landing the schema bump under task058.
3. **Multi-turn Hermes — env-side wiring:** the `general_tool_calling` env
   currently sets `max_turns=2` (singleturn-friendly). The new
   `multi_turn_tool_use` env this PR adds sets `max_turns=10` and reuses the
   trajectory verifier; downstream NeMo-Gym side needs the same flag flipped
   before M1 RLVR can use it.
4. **Lean proof verification:** M0 only stores the proof statement +
   reference proof and verifies non-empty. Real Lean check needs the Lean
   toolchain in the sandbox — that's task017 / task049 territory.

## 7. What this PR delivers vs what remains

| Artifact | Status |
|---|---|
| `docs/m0-dataset-expansion-plan.md` | this file |
| `workspace/tasks/task056_m0_tier1_expansion/` | scaffolded; remaining tier-1 envs to land here |
| `workspace/tasks/task057_m0_tier2_expansion/` | scaffolded |
| `workspace/tasks/task058_production_dataset_slug_fixes/` | scaffolded; slug + naming bug fixes deferred to that task |
| 3 new M0 envs wired (NuminaMath, MuSiQue, multi-turn Hermes) | ✓ |
| 4 remaining tier-1 envs (structured output, Lean, SWE-pivot, tool-repair negatives) | ✗ — task056 |
| 6 tier-2 envs (SQL, terminal, safety, multilingual, long-context, math-with-tools) | ✗ — task057 |
| Production slug / subset / contamination fixes | ✗ — task058 |
