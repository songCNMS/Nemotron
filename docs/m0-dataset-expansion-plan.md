# M0 Data Foundation — Expansion Plan

Last updated: 2026-05-18 (refined against `main` at `4e95552`)

Companion to `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md`
(plan §3, §6, §7) and `docs/implementation-roadmap.md`. Scopes the remaining
M0 work needed to give M1+ a complete data foundation. Reflects `main` after
`task005_m1_sft_v0_scope_expansion` follow-up PRs landed terminal, short SWE
trace, tool-repair-negative, and structured-output envs; the M1 SFT JSONL →
packed Parquet round-trip smoke runner; and task056 Session 1 adding
NuminaMath, MuSiQue, and multi-turn Hermes.

## 1. State of `main` (`4e95552`)

**Eleven** M0 environments wired end-to-end (registry + JSONL contract +
oracle health gate + difficulty signal + M1 SFT supervision builder):

| Env | Source | Plan §7 family | Landed via |
|---|---|---|---|
| `search_grounded_qa` | `hotpotqa/hotpot_qa` distractor | Search / Browser | M0 baseline |
| `search_multihop_qa` | `dgslibisey/MuSiQue` | Search / Browser (multi-hop) | task056 Session 1 |
| `code_execution_python` | `google-research-datasets/mbpp` full | Code Generation | M0 baseline |
| `general_tool_calling` | `NousResearch/hermes-function-calling-v1` singleturn | Tool Use | M0 baseline |
| `multi_turn_tool_use` | `NousResearch/hermes-function-calling-v1` `func_calling` (multi-turn) | Tool Use (multi-turn) | task056 Session 1 |
| `math_reasoning_numeric` | `openai/gsm8k` main | Math / Reasoning | M0 baseline |
| `math_competition_numeric` | `AI-MO/NuminaMath-CoT` | Math / Reasoning (competition) | task056 Session 1 |
| `terminal_basic_shell` | `aelhalili/bash-commands-dataset` | Terminal / Workplace | task005 (PR e2d0bcd / 3e37616) |
| `swe_pivot_patch_supervision` | `princeton-nlp/SWE-bench_Lite` | SWE | task005 |
| `tool_call_repair_negative` | derived from Hermes singleturn (with `escape_tool_markup_for_prompt` so the invalid artifact survives chat-template rendering as quoted text instead of being interpreted as a real tool call) | Tool Use (negatives) | task005 (`3e37616` + `905de2d` markup-escape refinement) |
| `structured_outputs_json` | `NousResearch/hermes-function-calling-v1` json_mode_singleturn | Structured Output | task005 |

That clears 6 of plan §7's 10 family list (Search single-hop + multi-hop,
Code, Tool Use single-turn + multi-turn, Math grade-school + competition,
Terminal, SWE pivot, Structured Output) and 5 of the v0 capabilities plan
§8 names. Remaining gaps: Math (formal Lean), SQL, Safety, Long-context,
Multilingual.

### Round-trip smoke runner

`905de2d` added `src/nemotron/recipes/super3/milestones/m1_agentic_sft/run_m1_sft_roundtrip_smoke.py`
— a self-contained CPU-friendly validator that runs the M1 JSONL through the
Nano3 chat template + a deterministic local tokenizer + sequence packing,
writes a packed Parquet shard, and reads it back to check schema and loss
mask. It's the cheapest gate for "did I break the chat-template render or
the loss mask?" without booting the full Xenna pipeline. New env work
(task056 Session 2 / task057) should clear this smoke for every added env
via the `--require-environment` flag (see §5.7).

## 2. Production references uncovered during the original audit

These NVIDIA-published HF datasets are referenced by the production Super3
SFT / RL stack and are useful targets for future M0 expansion (each provides
clean license + revision pin and a published structure):

- `nvidia/Nemotron-Instruction-Following-Chat-v1` — `chat_if`,
  `structured_outputs` subsets (ODC-BY-1.0 / CC-BY-4.0; 431 K).
- `nvidia/Nemotron-Competitive-Programming-v1` — cpp / python / infinibyte
  (CC-BY-4.0; 3.9 M). Repo subset names use `_part00` not `.part_00` —
  `data_blend_raw.json` reference will fail until the dot vs underscore
  mismatch is fixed (task058).
- `nvidia/Nemotron-SWE-v1` — `r2e_gym` (CC-BY-4.0; 51 K). Possible overlap
  with SWE-Bench Verified; needs filter before SWE eval.
- `nvidia/Nemotron-Math-Proofs-v1` — Lean split (CC-BY-SA-4.0 ⚠;
  share-alike obligations cascade through derived artifacts; ~925 K).
- `nvidia/Nemotron-Agentic-v1` — `interactive_agent` (19 K) + `tool_calling`
  (316 K). CC-BY-4.0 + Apache-2.0.
- `nvidia/Nemotron-RL-Super-Training-Blends` — RLVR1 (139 K) / RLVR2
  (156 K) / RLVR3 (107 K) / SWE1 (51 K) / SWE2 (1.4 K) / RLHF (25 K).
  **Current code refers to `Nemotron-3-Super-RL-Training-Blends` (with a
  `-3-`) — that slug 404s; the live repo dropped the `-3-`.** Tracked by
  task058.
- `BytedTsinghua-SIA/DAPO-Math-17k` (Apache-2.0; 1.79 M). **No benchmark
  scrub documented** — any M1 RLVR using it should add a MATH / AIME / GSM8K
  decontamination pass.
- `Skywork/Skywork-OR1-RL-Data` math + code splits (license unstated; flag
  for legal review). Decontaminated vs AIME-24/25 and LiveCodeBench by
  upstream.

## 3. Gap analysis, prioritized

Priority criteria:
- (a) blocks a downstream M1 RL stage with no clean workaround
- (b) explicitly named in plan §7 as one of the ten families
- (c) has a clean public dataset with a permissive license

### Tier 1 — high priority, clean fits (remaining work: task056)

| Env id (M0) | HF source | License | Rows | Verifier | Status |
|---|---|---|---|---|---|
| `math_competition_numeric` | `AI-MO/NuminaMath-CoT` | Apache-2.0 | 859 608 | `normalized_exact_or_contains` (matches the `\boxed{…}` answer span) | ✓ — task056 Session 1 |
| `search_multihop_qa` | `dgslibisey/MuSiQue` (Ans) | CC-BY-4.0 | 24 814 | `normalized_exact_or_contains` (mirrors HotpotQA verifier) | ✓ — task056 Session 1 |
| `multi_turn_tool_use` | `NousResearch/hermes-function-calling-v1` (`func_calling` config) | Apache-2.0 | reuses existing pin | `tool_schema_and_argument_match` + trajectory check | ✓ — task056 Session 1 |
| `math_formal_lean` | `nvidia/Nemotron-Math-Proofs-v1` (Lean split) | CC-BY-SA-4.0 ⚠ | ~925 K | new `lean_proof_stub` verifier (M0 stage only checks non-empty) | ✗ — task056 Session 2 (blocked on legal/share-alike clearance) |
| `structured_outputs_json` | `NousResearch/hermes-function-calling-v1` (`json_mode_singleturn`) | Apache-2.0 | reuses existing pin | `json_value_exact_match` | ✓ — landed via task005 |
| `terminal_basic_shell` | `aelhalili/bash-commands-dataset` | MIT | 100 train / 25 val | `command_substring_match` | ✓ — landed via task005 |
| `swe_pivot_patch_supervision` | `princeton-nlp/SWE-bench_Lite` | source-repo-specific | 100 train / 20 val | `patch_diff_match` | ✓ — landed via task005 |
| `tool_call_repair_negative` | derived from Hermes singleturn | Apache-2.0 | ≤ 100/env | `negative_recognition` | ✓ — landed via task005 |

Only `math_formal_lean` remains, and it's blocked on the §6 share-alike
question (CC-BY-SA-4.0 — obligation cascades through any derived artifact).
Once legal/product clears it, the wiring is a single follow-up PR
(converter + new `lean_proof_stub` verifier + an `assistant_for_lean_proof`
M1 supervision builder).

### Tier 2 — plan-§7 mandated, each has a notable contamination or licensing concern (task057)

| Env id (M0) | HF source | License | Concern |
|---|---|---|---|
| `sql_text_to_query` | `birdsql/bird_mini_dev` (3 dialects) + `bird-bench/bird` train | CC-BY-SA-4.0 ⚠ | `mini_dev` is the BIRD eval slice — keep held out |
| `terminal_advanced_shell` | extension to current `terminal_basic_shell` (CLI-1M or longer-form bash) | TBD | task005 wired a smoke-scale terminal env; a deeper corpus is needed for M2 |
| `safety_reasoning_smoke` | `nvidia/Nemotron-Content-Safety-Reasoning-Dataset` | CC-BY-4.0 | Viewer schema issues — loader validation needed |
| `multilingual_instruct` | `CohereLabs/aya_dataset` (204 K human-written) | Apache-2.0 | Avoid `aya_collection` (has translated FLAN → XNLI/XQuAD overlap risk) |
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

1. **HF slug fix:** `stage2_rl/data_prep.py` and `_data_prep_base.py` point
   at `nvidia/Nemotron-3-Super-RL-Training-Blends`. The live repo is
   `nvidia/Nemotron-RL-Super-Training-Blends`. Current path 404s.
2. **Subset naming:** `stage1_sft/config/data_prep/data_blend_raw.json` uses
   `competitive_coding_cpp.part_00` (dot); the HF repo uses `_part00`
   (underscore, no dot). Loader will fail.
3. **Skywork-OR1-RL-Data missing license** on the HF card — flag for legal
   review before any commercial RL run.
4. **DAPO-Math-17k contamination:** no benchmark scrub documented. Add
   `contamination_against` metadata + an explicit decontamination pass
   before any M1 RLVR launches against MATH / AIME / GSM8K eval.

## 5. Wiring rules — what counts as "wired" at M0

For each new env, the same seven-point checklist (matching the eleven envs
currently on main):

1. `data_registry.yaml` entry with `hf_dataset`, `hf_config`,
   `hf_revision`, `hf_split`, optional `hf_val_split`, `license`, `domain`,
   `reward_type`, `contamination`, `use_stage`.
2. `environment_registry.yaml` entry with reward verifier, range, semantics,
   resource budget, telemetry list, health-check `min_rows_per_split` and
   `required_fields`.
3. Converter function in `prepare_m0_assets.py` that produces a NeMo-Gym
   record matching the M0 JSONL contract; registered in `CONVERTERS`.
4. System prompt entry in `SYSTEM_PROMPTS` if the env needs a non-shared
   prompt.
5. Verifier registration in `run_m0_health_baseline.py` (or proof that an
   existing verifier suffices).
6. M1 SFT supervision builder (`assistant_for_*` or the tool-trajectory
   path) in `prepare_m1_agentic_sft.py` so the M1 entry can consume the new
   env; plus an entry in `M1_USE_BY_ENV` so the metadata reflects the
   actual skill the row exercises.
7. **Round-trip smoke clean** —
   `python src/nemotron/recipes/super3/milestones/m1_agentic_sft/run_m1_sft_roundtrip_smoke.py --require-environment <new_env_id>`
   must succeed against the prepare_m1 output. This catches chat-template
   render breaks, loss-mask drift, and any `<tool_call>` / `<tool_output>`
   markup that would be eaten by Jinja before the M1 SFT loss sees it
   (`tool_call_repair_negative` hit this at `905de2d`; the fix was the new
   `escape_tool_markup_for_prompt` helper, which any future env producing
   adversarial markup should reuse).

The eleven existing envs all follow this pattern and serve as concrete
references for new env work.

## 6. Open questions to resolve before tier-2 / tier-3 work

1. **Share-alike posture:** are CC-BY-SA-4.0 sources (Nemotron Lean proofs,
   BIRD SQL) acceptable? Share-alike obligations cascade through any
   derived artifact (eval reports, distilled SFT data).
2. **Contamination policy:** every M0 source used in M1+ eval must be
   deduped against M0 train + val. Recommend adding a
   `contamination_against` field on each spec; landing the schema bump
   under task058.
3. **Multi-turn Hermes — env-side wiring:** the new `multi_turn_tool_use`
   env (task056) needs NeMo-Gym's max_turns and trajectory verifier flipped
   before M1 RLVR can use it. The `general_tool_calling` env defaults to
   `max_turns=2`; the new env will need `max_turns=10` and stricter
   trajectory checking.
4. **Lean proof verification:** M0 only stores the proof statement +
   reference proof and verifies non-empty. Real Lean check needs the Lean
   toolchain in the sandbox — that's task017 / task049 territory.

## 7. Delivered vs remaining (as of `main` `4e95552`)

| Artifact | Status |
|---|---|
| `docs/m0-dataset-expansion-plan.md` | this file (originally landed via #22 / `60896a7`, refined since for round-trip smoke + escape-markup + 3 new Tier-1 envs) |
| `workspace/tasks/task056_m0_tier1_expansion/` | scaffolded; 1 remaining Tier-1 env (`math_formal_lean`) for Session 2 |
| `workspace/tasks/task057_m0_tier2_expansion/` | scaffolded |
| `workspace/tasks/task058_production_dataset_slug_fixes/` | scaffolded; slug + naming bug fixes deferred to that task |
| 4 of 8 Tier-1 envs (terminal, SWE-pivot, tool-repair negatives, structured-output) | ✓ — landed independently via task005 on main |
| `run_m1_sft_roundtrip_smoke.py` validator | ✓ — landed via task005 (`905de2d`); now a required wiring step (§5.7) |
| `escape_tool_markup_for_prompt` helper for negative-example prompts | ✓ — task005 refinement (`905de2d`); reusable for any future env that emits chat-template-sensitive markup |
| 3 Tier-1 envs from task056 Session 1 (NuminaMath, MuSiQue, multi-turn Hermes) | ✓ — task056 Session 1 (`4e95552`) |
| 1 remaining Tier-1 env (`math_formal_lean`) | ✗ — task056 Session 2, blocked on §6 share-alike clearance |
| 6 Tier-2 envs (SQL, terminal v2, safety, multilingual, long-context, math-with-tools) | ✗ — task057 |
| Production slug / subset / contamination fixes | ✗ — task058 |
