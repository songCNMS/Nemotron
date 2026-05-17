# M1 Agentic SFT v0 — Review Findings

Reviewer: intern_nemontron_review_cc
Date: 2026-05-17
Scope: commit range `47cb0ee..HEAD` (post M0 task001/task002 merge), focused on PR #3 / #6 / #7
Reference: `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §3 / §4 / §5.1 / §6 / §8

Files inspected:

- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/README.md`
- `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_smoke.yaml`
- `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`
- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml`
- `src/nemotron/recipes/super3/smoke_runtime.py`
- `src/nemotron/recipes/super3/tiny_model.py`
- `src/nemotron/recipes/super3/stage0_pretrain/{config/tiny_smoke.yaml, test_train.py}`
- `src/nemotron/recipes/super3/stage1_sft/{test_train.py, train.py}`
- `tests/recipes/super3/test_m1_agentic_sft.py`
- M0 fix commit `126222e` (`Fix M0 subset overwrite and M1 tool SFT conversion`)

Run: `PYTHONPATH=src pytest tests/recipes/super3/` → 32 passed.

---

## Priority summary

| Level | # | Topic |
|---|---|---|
| P0 (run-blocker / cross-intern) | #1 | cross-intern repo dir in planner default |
| P0 | #2 | default `global_batch_size=4` incompatible with default `gpus_per_node=8` |
| P1 (training-data correctness) | #3 | GSM8K `####` marker leaks into SFT reasoning target |
| P1 | #4 | no empty-content guard on supervision messages |
| P1 | #11 | `search_grounded_qa` supervision is a bare short answer; no grounding pattern |
| P1 | #14 | `tool` role loss-mask behavior not verified end-to-end |
| P2 (plan gap) | #5 | SWE / terminal / structured-output absent from v0 |
| P2 | #6 | no negative examples (malformed tool / hallucinated tool output) |
| P2 | #7 | no difficulty curriculum / pass-rate filtering |
| P2 | #10 | `metadata.m1_use` name-mismatched and hardcoded across records |
| P3 (tech debt / clarity) | #8, #9, #12, #13, #15–#24 | see below |

---

## P0 — Run-blocker / cross-intern leakage

### #1 `plan_m1_agentic_sft_training.py:27` `DEFAULT_REPO_DIR` points to another intern's worktree

```python
DEFAULT_REPO_DIR = Path("/work-agents/intern_nemontron_code_reading/Nemotron")
```

Any intern who runs the planner without `--repo-dir` produces a `run_m1_agentic_sft.sh` whose first line is `cd /work-agents/intern_nemontron_code_reading/Nemotron`. That walks the training job into another intern's working tree — polluting in-progress branches and racing with their git state. The default needs to be either:

- the repo root resolved from `Path(__file__)` walking up the tree, or
- `${PWD}` / a documented env var, or
- removed entirely so the flag is required.

### #2 Default GBS=4 × GPUs=8 × MBS=1 violates `GBS ≥ DP × MBS`

`plan_m1_agentic_sft_training.py:369-370` plus `:365`:

```python
parser.add_argument("--gpus-per-node", type=int, default=8)
parser.add_argument("--global-batch-size", type=int, default=4)
parser.add_argument("--micro-batch-size", type=int, default=1)
```

With no TP/PP overrides DP = 8, so each rank would need < 1 micro batch — Megatron asserts on this during model+optimizer setup and the job never reaches the first step. `m1_agentic_train.yaml:32 global_batch_size: 4` carries the same value.

Either bump the default GBS to ≥ 8 (a multiple of DP × MBS) or default `gpus_per_node` to 1 and document the multi-GPU override.

---

## P1 — Training-data correctness

### #3 GSM8K `#### N` verifier marker leaks into reasoning SFT target

`prepare_m1_agentic_sft.py:assistant_for_reasoning`:

```python
reference = record.get("extra_env_info", {}).get("reference_solution")
if reference is None:
    reference = record.get("expected_answer", "")
return {"role": "assistant", "content": str(reference).strip()}
```

`extra_env_info.reference_solution` is M0's untouched GSM8K `answer` field, which keeps the `#### 24` benchmark separator. The cleaned numeric value lives in `expected_answer` (normalized by `normalize_numeric_answer`). The SFT target therefore teaches the model to literally emit `####`, a verifier marker, on every reasoning task — that pattern then escapes GSM8K-shaped data and shows up on unrelated math prompts at inference time.

Suggested fix: prefer `expected_answer` for reasoning supervision, or strip `####\s*` from `reference_solution`.

### #4 No empty-content guard on supervision messages

`convert_m0_record` does not verify that the assistant message has either non-empty `content` or non-empty `tool_calls`. If any future M0 row arrives with both `reference_solution` and `expected_answer` empty, SFT will silently train on `{"role":"assistant","content":""}` (loss_mask = 1, target = EOS only). M0 task001's hermes path already added the same defensive `raise ValueError`; mirror it here.

### #11 `search_grounded_qa` supervision is a bare short answer; no grounding pattern

`assistant_for_search` outputs `{"content": expected_answer.strip()}`, e.g. literally `"London"`. plan §8 calls out "search pattern" as a v0 goal, by which it means a "look at passages → cite → answer" template. A one-word target teaches the model neither passage attention nor citation form. Suggested supervision shape:

```
Answer: <ans>
Evidence: [n] <one supporting sentence>
```

— even fixed-format templating is better than the current bare answer.

### #14 `tool` role loss-mask behavior is not verified

plan §5.1 prescribes `system/user loss_mask=0, assistant=1` but is silent on `tool`. Convention is `tool=0` (environment output, not the policy). `prepare_m1_agentic_sft.py` emits `{"role":"tool", ...}` into `messages`; `agentic_v0.yaml` does not configure tool masking and `chat_template: nano3` is reused unchanged from non-agentic flow. Concretely:

- Inspect what `PackedSftParquetStage` + nano3 chat template emit for a tool message — is the role boundary captured and `loss_mask=0` applied?
- If not, the trajectory turns under #15 (commit 126222e) will train the model to imitate tool outputs.

Add either a render-side assertion in `tests/recipes/super3/test_m1_agentic_sft.py` (`render → assert loss_mask == 0 for tool tokens`) or a config field that explicitly masks tool messages.

---

## P2 — Plan vs implementation gaps

### #5 Coverage shortfall: SWE / terminal / structured-output absent

plan §8 lists v0 as "tool-call syntax · terminal basics · search pattern · structured output · 短 SWE traces". The implementation only sources four M0 environments (`search`, `code`, `general_tool_calling`, `math_reasoning_numeric`). Concretely missing:

- terminal basics — no terminal_pivot or shell env in M0 either.
- structured output (strict JSON / schema adherence beyond function-calling) — `code_execution_python` is close but not the same.
- short SWE traces — no SWE env in M0; plan §5.4 / §5.5 only kicks in after M1 RL.

If the v0 scope is intentionally narrowed, README should say so explicitly. Otherwise the M0 env registry needs the three missing families before M1 Agentic SFT v0 is complete.

### #6 No negative examples

plan §8: "加入 malformed tool call、hallucinated tool output 等负例". Current implementation has only positive supervision. `convert_m0_record` tags a record with `metadata.warning = "missing expected tool_calls"` when general_tool_calling has no tool calls, but does not deliberately construct negatives.

Suggested follow-up: at v0 supervision time, mix in a small fraction (~5%) of intentionally malformed records (broken JSON, hallucinated tool name) with assistant supervision teaching the recovery pattern (apologize + retry with valid call).

### #7 No difficulty curriculum / pass-rate filtering

plan §6: "先用当前 SFT 模型过滤掉稳定做对的样本，再按 pass rate、judge confidence、rollout length 排序". `prepare_m1_agentic_sft.py` takes all M0 train rows verbatim, ignores M0's `health_baseline/health_baseline_report.json` even though oracle pass/fail is available, and emits a single blend entry with `weight: 1.0`. Curriculum stratification is the explicit M1 → M2 lever; v0 should at least lay the metadata.

### #10 `metadata.m1_use` is hardcoded and name-mismatched

`prepare_m1_agentic_sft.py:195-200`:

```python
"m1_use": [
    "tool call syntax",
    "search grounded answer format",
    "code solution format",
    "reasoning answer format",
],
```

Two problems:

1. Same 4 strings on every record regardless of environment — should be per-row narrowed.
2. "search grounded answer format" is false advertising: see #11, the supervision is a bare short answer, not a grounded format.

Also missing here vs plan §8: `terminal basics`, `structured output`, `short SWE traces`, `negative repair`.

---

## P3 — Clarity / tech debt

### #8 Chat template still pinned to `nano3`

`agentic_v0.yaml:37 chat_template: nano3`; README says "reuses the checked-in Nano3 template implementation for tool call rendering until a separate Super3 template is added". plan §5.1 says reasoning-mode / chat template should align with Super3. Acknowledged TODO; track explicitly so it does not leak into M1 final.

### #9 plan §5.1 two-stage SFT loss (token-level → sample-level) is not implemented

`m1_agentic_train.yaml` uses only next-token loss with assistant mask via `packed_sequence_specs`. Acceptable for v0, but the README / config comment should explicitly state "two-stage SFT loss deferred to v1+" so the next reviewer doesn't re-discover it.

### #12 M0 `used_in` lineage is dropped

M0 records carry `used_in: ["M0 data_env_foundation", "M1 RLVR ..."]` (stage lineage). M1 overwrites the field with `["super3", "super3_agentic_sft_v0", "m1_agentic_sft_v0"]`. Lineage / contamination tracking later will need the original M0 stages; preserve as `metadata.m0_use_stage`.

### #13 Tool-calling system prompt replacement is asymmetric

`prompt_messages` only rewrites system for `general_tool_calling` (replaces M0's per-env system with a single canonical line). Other envs keep their M0-prepared system text. Intentional (commit 126222e) to scrub Hermes `<tools>[]</tools>` content, but downstream readers will trip over the inconsistency. Document this in the README "Supervision Mapping" table.

### #15 Assistant supervision may carry `content=""` + `tool_calls=[...]`

`trajectory_for_tool_calling` emits `{"role":"assistant","content":"","tool_calls":[...]}` when an assistant turn is pure tool emission. Most chat templates render this correctly, but nano3 in particular has not been asserted to do so. Add a `tests/recipes/super3/` test that renders such a message through `PackedSftParquetStage`'s chat path and verifies the produced token sequence.

### #16 Hardcoded `/mnt/3fs/data/lei.song/...` and per-intern paths

Multiple defaults are pinned to one intern's home:

- `prepare_m1_agentic_sft.py:19 DEFAULT_M0_INPUT_DIR`
- `plan_m1_agentic_sft_training.py:20 DEFAULT_PACKED_SFT_DIR`
- `plan_m1_agentic_sft_training.py:23 DEFAULT_OUTPUT_DIR`
- `plan_m1_agentic_sft_training.py:24 DEFAULT_SAVE_DIR`
- `plan_m1_agentic_sft_training.py:27 DEFAULT_REPO_DIR` (also #1)

Switch to `${PWD}`-relative defaults or required flags.

### #17 `m1_agentic_train.yaml:32 train_iters: 1700` is grossly over-sized for M0 smoke data

100/env × 4 envs ≈ 400 raw rows → ~5–20 packed sequences at pack_size 4096. GBS=4 → ~5 iters covers a full epoch. Default 1700 = ~350 epochs of overfitting if anyone runs the config without first invoking the planner. Either lower the default or add a startup assertion / warning that the planner output should be sourced first.

### #18 `smoke_runtime.patch_dataset_helper_compile_if_prebuilt` silently no-ops on import failure

`try / except Exception: return` — if `helpers_cpp` is missing AND the Makefile is also missing, training still fails with "Makefile not found" at first step. The patch is useful only when `helpers_cpp` is already importable. Add `logger.warning("dataset helpers patch skipped: %s", exc)` to make the failure mode visible.

### #19 `tiny_model.py` silently degrades Super3 → Nano3 provider

The `try / except ImportError` fallback uses `Nemotron3NanoProvider` when `Nemotron3SuperProvider` is unavailable. The docstring still claims "preserves every Super3-unique feature at minimal scale" — false after the fallback. Add `logger.warning("Super3 provider missing; tiny model uses Nano3 base — Super3-specific tests are no longer Super3-shaped")` and surface the active base class in the smoke run output.

### #20 user-content `<tool_call>` / `<tools>` blocks not scrubbed

The system-prompt cleanup in `prompt_messages` (commit 126222e) only sanitizes `system`. user content from Hermes that includes demo `<tool_call>` blocks survives into SFT input. Either run `strip_tool_call_blocks` on user content too, or assert in a test that user content never contains `<tool_call>`.

### #21 `compute_train_iters` derived-rows path is uncovered

`tests/recipes/super3/test_m1_agentic_sft.py:test_plan_m1_training_writes_manifest_and_run_script` writes `b"not-a-real-parquet"` shards; `maybe_count_parquet_rows` returns None, and the test only exercises the explicit `train_iters` path. Add a tiny real-parquet fixture (1 row) so the "infer from packed rows" arm gets coverage.

### #22 No end-to-end test for prepare_m1 → super3 data prep sft → planner

Each leg is tested in isolation, but no test stitches them together. A minimal stub pipeline (mock packed_sft_dir + minimal metadata.json) verifying the planner can consume what prepare_m1 produces would catch field-name drift early.

### #23 `m1_agentic_smoke.yaml` lacks a config-schema test

The full-train yaml is indirectly covered by planner tests; the smoke yaml only appears in the README. Add a yaml-loading + required-fields test to prevent silent drift.

### #24 M0 `cleanup_stale_split_files` semantics under-documented (commit 126222e)

The new stale-cleanup logic in `prepare_m0_assets.py` is correct, but `--overwrite` now both replaces active files AND deletes stale env directories. The README / `--overwrite` help string still reads as "overwrite target files generated by this script"; mention the new destructive behavior.

---

## Recommended next actions

1. P0 first: open a focused follow-up PR fixing #1 (cross-intern repo dir) and #2 (GBS×DP defaults). Both are one-liners.
2. P1 batch: another PR for #3 (GSM8K `####`), #4 (empty-content guard), #11 (search supervision template), #14 (tool loss-mask verification + test).
3. P2 plan-gap items: surface as task / Linear issues against the M0/M1 owners; they imply data-source additions that are outside a single PR.
4. P3 items can be folded into the next M1 milestone PR or its README cleanup pass.
