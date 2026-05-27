# Qwen4B V7 2k Pilot Session 88

## Setup

- Run: `task071_qwen4b_hard_math_long_reasoning_v7_pilot_2k`
- Strategy: `hard_math_long_reasoning_v7`
- Qwen source: `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`
- Megatron seed checkpoint: `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`
- Pack/sequence length: `8192/8192`
- Data cap: `2000` train and `100` val rows per M0 dataset
- Training shape: `2` GPUs, global batch size `2`, micro batch size `1`, lr `2e-7`, min lr `8e-8`, warmup `20`

## Data Prep

- M1 train rows: `14045`
- M1 val-shadow rows: `513`
- M0 train rows by slice: search grounded QA `2000`, search multihop QA `2000`, math reasoning numeric `2000`, math competition numeric `2000`, code execution Python `374`, terminal basic shell `840`, SWE pivot patch supervision `300`, general tool calling `1100`, multi-turn tool use `1100`, tool-call repair negative `1090`, structured JSON outputs `1241`
- V7 hard verified source/written rows: `29/29`
- V7 broad verified source/written rows: `1262/0`
- V7 final-answer aux source/written rows: `1/0`
- V7 format-repair source/written rows: `2708/0`
- V7 heldout eval rows: `200`
- Packed artifact: `13901` sequences, `13960245` tokens, `8` shards
- Packed train/valid rows: `1070/211`
- Planned train iters: `428`
- Packed contract: `chat_template=tokenizer`, `enable_thinking=false`, `truncate_history_thinking=false`

## Training

- Remote run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_long_reasoning_v7_pilot_2k`
- Final checkpoint: `checkpoints/iter_0000428`
- Validation points:
  - iter `200`: loss `0.6374835`, PPL `1.891714`
  - iter `400`: loss `0.4642023`, PPL `1.590745`
  - iter `428`: loss `0.4411893`, PPL `1.554555`
- Health: skipped iterations `0`, nan iterations `0`
- Local train log: `outputs/task071_qwen4b_hard_math_long_reasoning_v7_pilot_2k/train_remote.log`
- Metric figure: `outputs/task071_qwen4b_hard_math_long_reasoning_v7_pilot_2k/metrics/metric_curves_session88_final_iter428.png`

## Export

- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_long_reasoning_v7_pilot_2k/hf_export_iter_0000428`
- Model id: `task071-qwen3-4b-agentic-sft-hard-math-long-reasoning-v7-pilot-2k-iter0000428-hf`
- Export manifest copy: `debug/task071_eval_logic_debug/qwen4b_v7_2k_iter428_session88/task071_export_manifest.json`
- Export validation: `model_type=qwen3`, `num_hidden_layers=36`, `3` safetensors shards, tokenizer chat template present

## Corrected Eval Gate

- Endpoint: SGLang on NemTron, `max_model_len=8192`
- MMLU-Pro corrected per-category-5: `35/70`, accuracy `0.5`, parsed rate `1.0`
- AIME25 corrected 10 rows at `max_tokens=6144`: parsed `6/10`, correct `0/10`, exact-normalized accuracy `0.0`, all finishes `length`, avg completion tokens `6144`
- HMMT corrected 10 rows at `max_tokens=6144`: parsed `6/10`, correct `1/10`, exact-normalized accuracy `0.1`, exact-normalized correct percent `10.0`, avg completion tokens `5042.2`
- Local copied summaries:
  - `debug/task071_eval_logic_debug/qwen4b_v7_2k_iter428_session88/corrected_eval_gate/mmlu_corrected_percat5/summary.json`
  - `debug/task071_eval_logic_debug/qwen4b_v7_2k_iter428_session88/corrected_eval_gate/math_corrected_10each_6144/summary.json`

## Decision

The larger V7 pilot increased hard rows from `3` to `29`, trained for `428` iterations instead of `12`, and reduced validation loss cleanly through the final checkpoint. The corrected math gate shows partial AIME parse recovery under a larger output cap, but AIME correctness remains `0/10`.

The 30B scale-up gate is not passed. The required condition before any 30B scale-up is AIME parsed recovery and AIME correct recovery on the pilot gate; this run satisfies parsed recovery but fails correct recovery. Do not start a 30B V7 scale-up from this recipe.

Recommended next recipe work:

- Increase the number of long, verified AIME/HMMT-style full-solution rows beyond the current `29` hard rows before packing.
- Filter out hard rows whose solution traces are long but not reliably answer-directed or whose boxed answer is not at the tail.
- Add a 4B pilot gate that requires AIME `correct_rows > 0` before exporting a 30B training script.
- Keep the 6144 or larger math eval cap for 8192-context 4B pilots so parse failures are not confused with short generation caps.
