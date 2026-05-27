# Qwen4B V7 Pilot Session 87

## Setup

- Run: `task071_qwen4b_hard_math_long_reasoning_v7_pilot`
- Strategy: `hard_math_long_reasoning_v7`
- Qwen source: `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`
- Megatron seed checkpoint: `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`
- Pack/sequence length: `8192/8192`
- Pilot data cap: `100` train and `25` val rows per M0 dataset

## Data Prep

- M1 train rows: `1100`
- M1 val-shadow rows: `273`
- V7 hard verified source/written rows: `3/3`
- V7 broad verified source/written rows: `63/0`
- V7 final-answer aux rows: `0`
- V7 format-repair source/written rows: `134/0`
- V7 heldout eval rows: `50`
- Packed artifact: `1088` sequences, `946089` tokens, `8` shards
- Packed train rows: `76`
- Planned train iters: `12`

## Training

- Remote run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_long_reasoning_v7_pilot`
- Final checkpoint: `checkpoints/iter_0000012`
- Final validation: loss `1.139335`, PPL `3.124691`
- Health: skipped iterations `0`, nan iterations `0`
- HF export: `hf_export_iter_0000012`
- Export manifest: `debug/task071_eval_logic_debug/qwen4b_v7_iter12_session87/task071_export_manifest.json`
- Metric figure: `outputs/task071_qwen4b_hard_math_long_reasoning_v7_pilot/metrics/metric_curves_session87_final_iter12.png`

## Smoke Eval

- Endpoint: SGLang on NemTron, `max_model_len=8192`
- MMLU-Pro corrected per-category-5: `35/70`, accuracy `0.5`, parsed rate `1.0`
- AIME25 corrected 5 rows: `0/5`, parsed rate `0.0`, all `length`, avg completion tokens `4096`
- HMMT corrected 5 rows: `2/5`, parsed rate `0.4`, exact-normalized accuracy `0.4`, avg completion tokens `3460.4`
- Local copied summaries:
  - `debug/task071_eval_logic_debug/qwen4b_v7_iter12_session87/corrected_eval_smoke/mmlu_corrected_percat5/summary.json`
  - `debug/task071_eval_logic_debug/qwen4b_v7_iter12_session87/corrected_eval_smoke/math_corrected_5each/summary.json`

## Decision

V7 smoke proves the 8192-token train/export/eval chain works and gives a nonzero HMMT signal on this tiny slice. It does not pass the AIME smoke gate: AIME outputs hit the 4096 generation cap without parseable final answers. The next pilot should increase V7 hard rows and train iters before 30B scale-up, and should add an AIME-specific stop/format check on a larger 4B or short 30B slice.
