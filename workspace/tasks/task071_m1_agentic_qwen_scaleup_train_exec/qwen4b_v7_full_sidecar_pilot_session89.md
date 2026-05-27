# Qwen4B V7 Full-Sidecar Pilot Session 89

## Code Changes

- Added `--math-sidecar-m0-input-dir` to M1 Agentic SFT prep so pilot runs can keep capped base agentic rows while sourcing math sidecar buckets from an uncapped M0 cache.
- Added planner wiring for `--math-sidecar-m0-input-dir`, `--math-sidecar-max-records-per-env`, and `--math-sidecar-max-val-shadow-per-env`.
- Tightened V7 hard-math row selection to require the last boxed answer to be scalar numeric, excluding symbolic/textual boxed conclusions that do not match AIME/HMMT numeric scoring.
- Added tests for scalar-numeric V7 filtering, uncapped math sidecar sourcing, and planner script emission.

## Pilot Setup

- Run: `task071_qwen4b_hard_math_long_reasoning_v7_full_sidecar_pilot`
- Base M0 cap: `2000/100` train/val rows per dataset
- Math sidecar source: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_balanced_v6/m0_agentic`
- Strategy: `hard_math_long_reasoning_v7`
- Pack/sequence length: `8192/8192`
- Qwen source: `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`
- Megatron seed checkpoint: `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`

## Data Prep

- Base M1 train rows: `14045`
- Base M1 val-shadow rows: `513`
- Sidecar source train rows scanned: math competition `859494`, math reasoning `7473`
- V7 hard verified source/written rows: `5702/5702`
- V7 verified full-solution source/written rows: `539265/0`
- V7 format-repair source/written rows: `321971/0`
- V7 final-answer aux source/written rows: `29/0`
- V7 heldout eval rows: `200`
- Packed artifact: `19574` sequences, `20958271` tokens, `8` shards
- Packed train/valid rows: `1402/211`
- Planned train iters: `561`

## Training

- Remote run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_long_reasoning_v7_full_sidecar_pilot`
- Final checkpoint: `checkpoints/iter_0000561`
- Validation points:
  - iter `200`: loss `0.6158555`, PPL `1.851240`
  - iter `400`: loss `0.4428872`, PPL `1.557197`
  - iter `561`: loss `0.3993315`, PPL `1.490828`
- Health: skipped iterations `0`, nan iterations `0`
- Metric figure: `outputs/task071_qwen4b_hard_math_long_reasoning_v7_full_sidecar_pilot/metrics/metric_curves_session89_final_iter561.png`

## Export

- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_long_reasoning_v7_full_sidecar_pilot/hf_export_iter_0000561`
- Model id: `task071-qwen3-4b-agentic-sft-hard-math-long-reasoning-v7-full-sidecar-pilot-iter0000561-hf`
- Export validation: `model_type=qwen3`, `num_hidden_layers=36`, `3` safetensors shards, tokenizer chat template present
- Export manifest copy: `debug/task071_eval_logic_debug/qwen4b_v7_full_sidecar_iter561_session89/task071_export_manifest.json`

## Corrected Eval

- MMLU-Pro corrected per-category-5: `35/70`, accuracy `0.5`, parsed rate `1.0`
- AIME/HMMT at 8k serving context and `6144` generation cap:
  - AIME25: parsed `3/10`, correct `0/10`, avg completion tokens `6129`
  - HMMT: parsed `5/10`, correct `3/10`, exact-normalized accuracy `0.3`, exact-normalized correct percent `30.0`
- AIME diagnostic at 16k serving context and `8192` generation cap:
  - AIME25: parsed `7/10`, correct `3/10`, exact-normalized accuracy `0.3`, avg completion tokens `7928.1`

## Decision

The larger V7 full-sidecar pilot passes the pilot AIME recovery gate only under the long-context protocol: `context_length=16384` with `aime_max_tokens=8192`. The earlier 8k/6144 gate still truncates most AIME rows and reports `0/10` correct, so future 30B promotion checks must use the 16k/8192 corrected math protocol.

A 30B scale-up script bundle has been generated but not launched:

- Output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar`
- Local data prep: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/run_local_data_prep.sh`
- Sync: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/sync_to_nemtron.sh`
- Remote train: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/run_nemtron_train.sh`

Launch condition: run the 30B script chain only when the serving/eval plan reserves a 16k corrected math gate for the exported 30B checkpoint.

## Verification

- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py`
- `pytest -q tests/recipes/super3/test_m1_agentic_sft.py -k "hard_math_long_reasoning_v7 or math_sidecar_can_use_uncapped_m0_source or packed_math_reasoning_tokens_before_box_are_supervised"` -> `3 passed, 73 deselected`
- `pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py -k "hard_math_long_reasoning_v7"` -> `1 passed, 11 deselected`
- `ruff check src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py`
