# M1 Agentic SFT v0 — Review Findings

Reviewer: intern_nemontron_review_cc

| Revision | Date | Against |
|---|---|---|
| v1 (original review) | 2026-05-17 | `47cb0ee..bd0ff62` — PR #3 / #6 / #7 |
| v2 (update) | 2026-05-17 | post-PR #10 / #8 — main at `19f682d` |
| v3 (this PR fixes) | 2026-05-17 | task004 — P0 #2 + N2 fixed, see PR #11 |
| v4 (this PR fixes) | 2026-05-17 | task006 — P1 #3 + N1 fixed, see PR #12 |
| v5 (this PR fixes) | 2026-05-17 | task007 — P1 #4 + #11 + #14 fixed, see PR #13 |

Plan reference: `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` §3 / §4 / §5.1 / §6 / §8.

Tests after update: `PYTHONPATH=src pytest tests/recipes/super3/ -q` → **56 passed + 1 skipped** (v1 baseline 32 → +13 from PR #10 → +4 from PR #11 → +3 from PR #12 → +5 from PR #13; the 1 skip is the optional `cosmos_xenna`-gated end-to-end loss-mask test).

Files inspected:

- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/README.md`
- `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_smoke.yaml`
- `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`
- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml`
- `src/nemotron/recipes/super3/stage1_sft/{train.py, qwen_local_train.py (new), test_train.py}`
- `src/nemotron/recipes/super3/smoke_runtime.py`
- `src/nemotron/recipes/super3/tiny_model.py`
- `src/nemotron/recipes/super3/stage0_pretrain/{config/tiny_smoke.yaml, test_train.py}`
- `src/nemotron/recipes/super3/milestones/m0_data_env/{prepare_m0_assets.py, run_m0_health_baseline.py, data_registry.yaml}`
- `scripts/import_qwen3_4b_local_to_megatron.py` (new in PR #8)
- `tests/recipes/super3/test_m1_agentic_sft.py`, `tests/recipes/super3/test_m0_*.py`

Status legend used below: ✓ Fixed · ◐ Partial · ✗ Still open · 📋 Tracked in another task.

---

## v2 status summary (24 v1 findings)

| # | Topic | v1 priority | v2 status |
|---|---|---|---|
| 1 | cross-intern repo dir in planner default | P0 | ✓ Fixed in PR #10 (`DEFAULT_REPO_DIR=None`, falls back to `Path.cwd()`) |
| 2 | `global_batch_size=4` × `gpus_per_node=8` × `mbs=1` violates GBS≥DP×MBS | P0 | ✓ Fixed in PR #11 task004 (`ensure_batch_geometry` guard in `build_plan`; default GBS bumped 4→8) |
| 3 | GSM8K `#### N` marker leaks into SFT reasoning target | P1 | ✓ Fixed in PR #12 task006 (`assistant_for_reasoning` prefers `expected_answer`; `_strip_gsm8k_marker` strips `####\s*` from fallback) |
| 4 | no empty-content guard on supervision messages | P1 | ✓ Fixed in PR #13 task007 (`_ensure_assistant_supervision_non_empty` in `convert_m0_record` now raises ValueError for every env when no assistant message has non-empty content or tool_calls; `assistant_for_search` returns empty content for empty answer so the guard fires uniformly) |
| 5 | SWE / terminal / structured-output absent from v0 | P2 | 📋 Tracked in `task005_m1_sft_v0_scope_expansion` |
| 6 | no negative examples (malformed tool / hallucinated tool output) | P2 | 📋 Tracked in `task005_m1_sft_v0_scope_expansion` |
| 7 | no difficulty curriculum / pass-rate filtering | P2 | ✗ Still open — not in any task |
| 8 | chat template pinned to `nano3` | P3 | ✗ Still open |
| 9 | two-stage SFT loss not implemented | P3 | ✗ Still open |
| 10 | `metadata.m1_use` hardcoded and name-mismatched | P2 | ✗ Still open — same 4 strings; "search grounded answer format" still false |
| 11 | `search_grounded_qa` supervision is a bare short answer | P1 | ✓ Fixed in PR #13 task007 — `assistant_for_search` now emits a grounded template referencing supporting-facts titles ("Based on the retrieved passages ([1] Title1, [2] Title2), the answer is …") |
| 12 | M0 `used_in` lineage dropped | P3 | ✗ Still open |
| 13 | tool-calling system-prompt replacement is asymmetric and undocumented | P3 | ✗ Still open |
| 14 | `tool` role loss-mask behavior not verified end-to-end | P1 | ✓ Fixed in PR #13 task007 — added `test_tool_role_supervision_survives_to_chat_template_input` (structural) + `test_tokenize_chunks_with_mask_pins_tool_role_to_zero` (end-to-end, `cosmos_xenna`-gated; auto-skipped in test envs without the full data-prep stack) |
| 15 | `content="" + tool_calls=[...]` render path untested at template level | P3 | ✗ Still open — structural tests only |
| 16 | hardcoded `/mnt/3fs/data/lei.song/...` and per-intern paths | P3 | ✓ Fixed in PR #12 task006 — M1 planner / prepare already moved to `None`/`../output/...` by PR #10; PR #8's Qwen entry default cleared (see **N1** below) |
| 17 | `train_iters: 1700` default oversized for M0 smoke data | P3 | ✗ Still open |
| 18 | `smoke_runtime.patch_dataset_helper_compile_if_prebuilt` silently no-ops on import failure | P3 | ✗ Still open |
| 19 | `tiny_model.py` silently degrades Super3 → Nano3 provider | P3 | ✗ Still open |
| 20 | user-content `<tool_call>` / `<tools>` blocks not scrubbed | P3 | ✗ Still open |
| 21 | `compute_train_iters` derived-rows path uncovered | P3 | ✗ Still open |
| 22 | no end-to-end test for prepare_m1 → super3 data prep sft → planner | P3 | ✗ Still open |
| 23 | `m1_agentic_smoke.yaml` lacks a schema test | P3 | ◐ Partial — new `test_m1_agentic_train_yaml_tokenizer_matches_data_prep_tokenizer` covers one field; full schema validation still missing |
| 24 | M0 `cleanup_stale_split_files` semantics under-documented | P3 | ✗ Still open |

Aggregate: **7 fixed (#1 by PR #10; #2 #N2 by PR #11; #3 #N1 #16 by PR #12; #4 #11 #14 by PR #13), 1 partial (#23), 11 still open, 2 tracked elsewhere.** PR #10 + PR #8 also introduced **3 new issues (N1–N3)** — N1 / N2 fixed; N3 still open. PR #10 brought **1 useful side-fix (T1)**.

---

## v2 — New findings since v1

### N1 — `qwen_local_train.py:25` re-introduces a `/mnt/3fs/data/lei.song/...` default (P3 #16 regression)

**Status (v4): ✓ Fixed in PR #12 task006** — `DEFAULT_QWEN_MODEL` removed; `resolve_qwen_hf_model()` now reads `SUPER3_M1_QWEN_HF_MODEL` and `raise ValueError` if unset, with a message pointing operators at the local-import script. Regression tests `test_qwen_local_train_requires_env_var` and `test_qwen_local_train_uses_env_var_when_set` cover both branches.

```python
DEFAULT_QWEN_MODEL = "/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507"
```

After v1's P3 #16 was largely cleaned up by PR #10 (planner / prepare defaults now relative or required), PR #8 added a debug entry that puts another intern's home directory back as the default Qwen weight path. Any intern who runs `python qwen_local_train.py` without `SUPER3_M1_QWEN_HF_MODEL` set will hit a "directory does not exist" deep inside the HF auto-bridge stack. Same drift class as v1 #16; suggested fix: leave the default as `None`, require either env var or CLI flag, and document the expected layout in the script docstring.

### N2 — `m1_agentic_smoke.yaml` now hard-requires `SUPER3_M1_PRETRAINED_CHECKPOINT` even when `finetune=false` (P1 regression)

**Status (v3): ✓ Fixed in PR #11 task004** — smoke yaml `pretrained_checkpoint` reverted to YAML literal `null`; full-train yaml keeps the strict `${oc.env:VAR}` form. Regression test `test_m1_agentic_smoke_yaml_pretrained_checkpoint_resolves_without_env` covers the fix.

PR #10 changed both smoke and full configs:

```yaml
# Omit the default so OmegaConf raises clearly when the env var is unset.
pretrained_checkpoint: ${oc.env:SUPER3_M1_PRETRAINED_CHECKPOINT}
```

The intent (catch the literal-`"null"` string trap that `${oc.env:VAR,null}` produces) is correct for `m1_agentic_train.yaml`. But `m1_agentic_smoke.yaml` has `finetune: false` — its purpose is to wire data loading + tiny-model training from random init, no pretrain checkpoint involved. `train.py:367` logs `cfg.checkpoint.pretrained_checkpoint` unconditionally, so OmegaConf raises `MissingMandatoryValue` even though nothing downstream uses the value. The documented offline smoke flow is now broken without setting an env var that the README never mentions.

Fix: in `m1_agentic_smoke.yaml`, write `pretrained_checkpoint: null` literally (YAML null, not `oc.env`); leave `m1_agentic_train.yaml` with the strict env-var resolution.

### N3 — `data_registry.yaml` newly enables `trust_remote_code: true` for hotpotqa with no operator-visible note

PR #10 added `trust_remote_code: true` to `m0_search_hotpotqa`. This is **required** (hotpotqa ships a custom loader script and `datasets>=2.16` refuses to run it otherwise), so the change itself is correct. But:

- M0 README's "Public Sources" table doesn't mention that one of the four sources now executes arbitrary Python from HF Hub at data-prep time.
- The only protection beyond the loader-script gate is the pinned `hf_revision`. If the revision is rotated later, the new loader runs unchecked.

Suggested follow-up: mark `trust_remote_code: true` rows in the M0 README, and add a one-line `SECURITY.md` / data-prep doc entry pointing at `hf_revision` as the only content guarantee.

### T1 (informational, not a finding) — `resolve_min_rows` + manifest `requested_rows`

PR #10 added a small useful feature: `prepare_m0_assets.py` writes `manifest["requested_rows"] = {"max_train_per_dataset", "max_val_per_dataset"}`, and `run_m0_health_baseline.py` caps the env spec's `min_rows_per_split` floor by what was actually requested. This stops the health gate from auto-failing legitimate 10-row smoke runs that fall below the registry's 25-row floor. Solid test coverage (`test_resolve_min_rows_caps_floor_to_requested_count`, `test_summarize_health_honors_requested_rows`). Calling out so it survives in the review record.

---

## Recommended next actions (revised)

1. **Still-open P0 / P1 — one focused PR each:**
   - #2 add `global_batch_size >= dp_size * micro_batch_size` assertion in `plan_m1_agentic_sft_training.build_plan` (where `dp_size = gpus_per_node * nodes // (tp_size * pp_size)`), and pick saner defaults (either `--global-batch-size 8` or `--gpus-per-node 1`).
   - #3 flip `assistant_for_reasoning` to prefer `expected_answer` for GSM8K; or strip `####\s*\d+` from `reference_solution` before emitting.
   - #4 raise (not warn) on empty supervision content/tool_calls for all environments, mirroring M0 task001's hermes path.
   - #11 template `search_grounded_qa` supervision into a grounded shape ("Answer: …\nEvidence: [n] …") instead of a bare short answer.
   - #14 add a render-time test that runs supervision through nano3 chat template + `PackedSftParquetStage` and asserts `loss_mask == 0` for tool-role tokens.
   - **N1** drop the lei.song Qwen default, require flag/env var.
   - **N2** revert `m1_agentic_smoke.yaml` to `pretrained_checkpoint: null` (YAML literal).
   - **N3** README/data-prep doc note on `trust_remote_code`.

2. **Plan gaps:** continue under `task005_m1_sft_v0_scope_expansion` (#5 / #6); separately scope #7 difficulty curriculum.

3. **Tech debt:** P3 items can fold into the next M1 scope-expansion or planner cleanup PR.

---

## v1 (original review — kept for traceability)

The v1 detail for findings 1–24 below is preserved verbatim as historical record. v2 statuses above are the authoritative state.

### P0 — Run-blocker / cross-intern leakage

#### #1 `plan_m1_agentic_sft_training.py:27` `DEFAULT_REPO_DIR` points to another intern's worktree

```python
DEFAULT_REPO_DIR = Path("/work-agents/intern_nemontron_code_reading/Nemotron")
```

Any intern who runs the planner without `--repo-dir` produces a `run_m1_agentic_sft.sh` whose first line is `cd /work-agents/intern_nemontron_code_reading/Nemotron`. That walks the training job into another intern's working tree — polluting in-progress branches and racing with their git state.

#### #2 Default GBS=4 × GPUs=8 × MBS=1 violates `GBS ≥ DP × MBS`

`plan_m1_agentic_sft_training.py:369-370` plus `:365`:

```python
parser.add_argument("--gpus-per-node", type=int, default=8)
parser.add_argument("--global-batch-size", type=int, default=4)
parser.add_argument("--micro-batch-size", type=int, default=1)
```

With no TP/PP overrides DP = 8, so each rank would need < 1 micro batch — Megatron asserts on this during model+optimizer setup and the job never reaches the first step.

### P1 — Training-data correctness

#### #3 GSM8K `#### N` verifier marker leaks into reasoning SFT target

`prepare_m1_agentic_sft.py:assistant_for_reasoning` prefers `extra_env_info.reference_solution` (raw GSM8K `answer` with `#### 24`). The cleaned numeric value in `expected_answer` is skipped. SFT therefore teaches the model to literally emit `####` on every reasoning task.

#### #4 No empty-content guard on supervision messages

`convert_m0_record` does not verify that the assistant message has either non-empty `content` or non-empty `tool_calls`. M0 task001's hermes path already added the same defensive `raise ValueError`; mirror it here.

#### #11 `search_grounded_qa` supervision is a bare short answer; no grounding pattern

`assistant_for_search` outputs `{"content": expected_answer.strip()}`, e.g. literally `"London"`. plan §8 calls out "search pattern" as a v0 goal — a one-word target teaches the model neither passage attention nor citation form.

#### #14 `tool` role loss-mask behavior is not verified

plan §5.1 prescribes `system/user loss_mask=0, assistant=1` but is silent on `tool`. Convention is `tool=0` (environment output, not the policy). `prepare_m1_agentic_sft.py` emits `{"role":"tool", ...}` into `messages`; `agentic_v0.yaml` does not configure tool masking and `chat_template: nano3` is reused unchanged.

### P2 — Plan vs implementation gaps

#### #5 Coverage shortfall: SWE / terminal / structured-output absent

plan §8 lists v0 as "tool-call syntax · terminal basics · search pattern · structured output · 短 SWE traces". The implementation only sources four M0 environments (`search`, `code`, `general_tool_calling`, `math_reasoning_numeric`). terminal, structured output, short SWE traces are absent.

#### #6 No negative examples

plan §8: "加入 malformed tool call、hallucinated tool output 等负例". Current implementation has only positive supervision.

#### #7 No difficulty curriculum / pass-rate filtering

plan §6: "先用当前 SFT 模型过滤掉稳定做对的样本，再按 pass rate、judge confidence、rollout length 排序". `prepare_m1_agentic_sft.py` takes all M0 train rows verbatim and ignores M0's `health_baseline_report.json`.

#### #10 `metadata.m1_use` is hardcoded and name-mismatched

```python
"m1_use": [
    "tool call syntax",
    "search grounded answer format",
    "code solution format",
    "reasoning answer format",
],
```

Same 4 strings on every record; "search grounded answer format" is false advertising (see #11).

### P3 — Clarity / tech debt

#### #8 Chat template still pinned to `nano3`

`agentic_v0.yaml:37 chat_template: nano3`; README acknowledges this as a TODO until a Super3 template is added.

#### #9 plan §5.1 two-stage SFT loss (token-level → sample-level) is not implemented

`m1_agentic_train.yaml` uses only next-token loss with assistant mask via `packed_sequence_specs`.

#### #12 M0 `used_in` lineage is dropped

M0 records carry `used_in: ["M0 data_env_foundation", "M1 RLVR ..."]`. M1 overwrites the field with `["super3", "super3_agentic_sft_v0", "m1_agentic_sft_v0"]` — preserve as `metadata.m0_use_stage`.

#### #13 Tool-calling system prompt replacement is asymmetric

`prompt_messages` only rewrites system for `general_tool_calling`. Document in README "Supervision Mapping" table.

#### #15 Assistant supervision may carry `content=""` + `tool_calls=[...]`

`trajectory_for_tool_calling` emits `{"role":"assistant","content":"","tool_calls":[...]}` when an assistant turn is pure tool emission. Add a template-render test.

#### #16 Hardcoded `/mnt/3fs/data/lei.song/...` and per-intern paths

Multiple defaults pinned to one intern's home — switch to `${PWD}`-relative defaults or required flags.

#### #17 `m1_agentic_train.yaml:32 train_iters: 1700` is grossly over-sized for M0 smoke data

Either lower the default or add a startup assertion / warning that the planner output should be sourced first.

#### #18 `smoke_runtime.patch_dataset_helper_compile_if_prebuilt` silently no-ops on import failure

Add `logger.warning("dataset helpers patch skipped: %s", exc)`.

#### #19 `tiny_model.py` silently degrades Super3 → Nano3 provider

Add `logger.warning("Super3 provider missing; tiny model uses Nano3 base")` and surface the active base class.

#### #20 user-content `<tool_call>` / `<tools>` blocks not scrubbed

The system-prompt cleanup in `prompt_messages` only sanitizes `system`. user content from Hermes that includes demo `<tool_call>` blocks survives into SFT input.

#### #21 `compute_train_iters` derived-rows path is uncovered

Tests write `b"not-a-real-parquet"` shards; `maybe_count_parquet_rows` returns None.

#### #22 No end-to-end test for prepare_m1 → super3 data prep sft → planner

Each leg is tested in isolation, but no test stitches them together.

#### #23 `m1_agentic_smoke.yaml` lacks a config-schema test

Add a yaml-loading + required-fields test to prevent silent drift.

#### #24 M0 `cleanup_stale_split_files` semantics under-documented (commit 126222e)

`--overwrite` now both replaces active files AND deletes stale env directories. README / `--overwrite` help string still reads as "overwrite target files generated by this script".
