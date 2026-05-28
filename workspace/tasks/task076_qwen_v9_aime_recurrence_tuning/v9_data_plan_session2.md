# V9 Data And Training Plan - Session 2

## Code Change

Added `hard_math_recurrence_v9` as a new Qwen hard-math sidecar strategy.

- Prep entrypoint: `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
- Planner entrypoint: `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py`
- Tests:
  - `tests/recipes/super3/test_m1_agentic_sft.py`
  - `tests/recipes/super3/test_m1_agentic_sft_math_decontamination.py`
  - `tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py`

V9 keeps the V8 clean-final prerequisite, then narrows the hard sidecar to rows with recurrence/counting structure:

- counting prompt signal such as binary strings, sequences, chairs, rows, ways, or consecutive constraints
- recurrence solution signal such as `dp[`, dynamic programming, recurrence, state, transition, or count
- run-length signal such as adjacent, consecutive, trailing, or run length

The strategy is included in the V7+ decontamination guard, so production prep requires `--decontaminate-math-against-corpus` unless the operator explicitly passes the skip flag.

## Local Source Count Probe

Scanned the existing V8 hard sidecar:

- Source: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/agentic_sft_v0_math_hard_verified_full_solution_train.jsonl`
- Rows scanned: `4546`
- V9 recurrence candidates: `220`

This is small enough to act as a focused sidecar and large enough not to be a single-problem patch.

## Decontamination Corpus

Generated a local prompt corpus for the V9 plan:

- Path: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- Total prompts: `1479`
- AIME25 prompts: `30`
- HMMT prompts: `30`
- MATH-style heldout-eval prompts: `1419`

Sources:

- AIME25 prompts from the local corrected-eval score-cache conversations.
- HMMT prompts from the local evaluator input artifact.
- MATH-style heldouts from the V8 `agentic_sft_v0_math_heldout_eval.jsonl` bucket.

## Generated V9 Plan

Generated a local scale-up plan without launching training:

- Output directory: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9`
- Manifest: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/scaleup_manifest.json`
- Local data prep: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_local_data_prep.sh`
- Remote train: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_nemtron_train.sh`
- Eval dry run: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_eval_basket_dry_run.sh`

Plan parameters:

- Strategy: `hard_math_recurrence_v9`
- Hard sidecar sample fraction: `1.0`
- Broad verified/full-answer/format-repair sidecars: `0.0`
- Math sidecar source: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/m0_agentic`
- Decontamination corpus: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- Pretrained checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`
- Sequence length / pack size: `8192 / 8192`
- Training length: `0.05` epochs
- LR: `8e-8`, min LR `3e-8`, warmup `20`
- GPUs: `0,1,2,3,4,5,6,7`, `nproc_per_node=8`

## Verification

Passed:

```bash
python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py
PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_agentic_sft_math_decontamination.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py::test_prepare_hard_math_long_reasoning_v7_keeps_long_verified_hard_rows tests/recipes/super3/test_m1_agentic_sft.py::test_prepare_math_sidecar_can_use_uncapped_m0_source tests/recipes/super3/test_m1_agentic_sft.py::test_prepare_hard_math_clean_final_v8_requires_single_expected_final_box tests/recipes/super3/test_m1_agentic_sft.py::test_prepare_hard_math_recurrence_v9_keeps_clean_dp_counting_rows
git diff --check
```

`ruff` is not installed in this container (`ruff` and `python -m ruff` both unavailable).

## Acceptance Mapping

This completes the second task076 acceptance criterion: V9 data/training plan generation now exists with explicit AIME25/HMMT/MATH-style heldout decontamination. Training has not been launched yet.
