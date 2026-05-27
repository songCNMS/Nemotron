# Qwen V6 Pilot And Full Launch Session 80

## Scope

User requested a small-data validation before scaling to full data, with the validation covering the complete flow from training through evaluation. This session added `hard_math_balanced_v6`, validated it on a Qwen3-4B pilot, then prepared uncapped V6 data and launched the formal Qwen3-30B-A3B run on NemTron.

## V6 Recipe

- Strategy: `hard_math_balanced_v6`.
- Hard sidecar: V5 high-precision verified full-solution filter.
- Diversity sidecar: broad verified full-solution replay restored.
- Extraction sidecars: small final-answer aux and format-repair samples.
- Default sampling fractions: hard `0.6`, broad verified `0.25`, final-answer aux `0.05`, format repair `0.03`.
- Planner support: `--math-v6-hard-verified-full-solution-weight`, `--math-v6-verified-full-solution-weight`, `--math-v6-final-answer-aux-weight`, `--math-v6-format-repair-weight`.

## Qwen4B Pilot

- Run: `task071_qwen4b_hard_math_balanced_v6_pilot`.
- Remote root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_balanced_v6_pilot`.
- Source HF model: `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`.
- Megatron checkpoint: `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`.
- Data cap: `max_train_per_dataset=100`, `max_val_per_dataset=25`.
- M1 rows: train `1100`, val-shadow `273`, errors `0`.
- V6 sidecar written rows: hard `11`, broad verified `12`, final-answer aux `0`, format repair `4`, heldout eval `50`.
- Packed rows: train `106`, valid `9`.
- Training plan: `train_iters=53`, GBS `2`, eval/save interval `20`.

## Pilot Train Metrics

- Final checkpoint: `iter_0000053`.
- Validation loss/PPL at iter `40`: `0.4337248 / 1.542994`.
- Final validation loss/PPL at iter `53`: `0.4315846 / 1.539695`.
- Max skipped/nan: `0/0`.
- Metric figure: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen4b_hard_math_balanced_v6_pilot/metrics/metric_curves_session80_pilot_final_iter53.png`.

## Pilot Export And Eval

- HF export: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen4b_hard_math_balanced_v6_pilot/hf_export_iter_0000053`.
- Model id: `task071-qwen3-4b-agentic-sft-hard-math-balanced-v6-pilot-iter0000053-hf`.
- Export size: about `7.6G`, 3 safetensors shards.
- Tokenizer: `Qwen2TokenizerFast`, chat template present.
- MMLU-Pro corrected per-category 5: `70` rows, accuracy `0.5142857142857142`, parsed rate `1.0`.
- AIME25 corrected 5 rows at `max_tokens=2048`: status ok `5/5`, parsed rate `0.8`, exact-normalized accuracy `0.0`.
- HMMT corrected 5 rows at `max_tokens=2048`: status ok `5/5`, parsed rate `0.2`, exact-normalized correct percent `0.0`.
- Eval sizing note: the default math cap `8192` exceeds the pilot endpoint context `4096` and returns HTTP 400; the `2048` cap validates the same runner against this pilot endpoint.

## Full V6 Data

- Output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_balanced_v6`.
- M0 uncapped train rows:
  - HotpotQA `90447`
  - MuSiQue `19938`
  - MBPP `374`
  - terminal bash commands `840`
  - SWE-bench Lite `300`
  - Hermes tool single-turn `1100`
  - Hermes tool multi-turn `1100`
  - Hermes repair negatives `1090`
  - Hermes JSON structured output `1241`
  - GSM8K `7473`
  - NuminaMath `859494`
- M1 base train rows: `983397`.
- M1 val-shadow rows: `11354`.
- V6 bucket source/written rows:
  - hard verified full-solution `114305 / 68583`
  - broad verified full-solution `430662 / 107666`
  - final-answer aux `29 / 1`
  - format repair `321971 / 9659`
  - heldout eval `1419 / 1419`
- Packed artifact: `1169133` total sequences, `769769392` tokens, train rows `61129`, valid rows `398`, `32` train shards.
- Qwen chat contract: `chat_template=tokenizer`, `enable_thinking=false`, `truncate_history_thinking=false`.

## Full Train Launch

- Remote root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_balanced_v6`.
- Tmux session: `task067_task071_qwen30b_a3b_hard_math_balanced_v6`.
- Train iters: `1529`.
- GPUs: all 8 H200.
- GBS: `8`.
- LR: `2e-7`, min LR `8e-8`, warmup `100`.
- Eval/save interval: `400`.
- Startup health: checkpoint loaded from `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/pretrained_megatron_qwen3_30b_a3b_instruct_2507`, GPUs active, no traceback.
- Latest synced metrics: iter `130/1529`, train loss `0.8720737`, load-balancing loss `1.476049`, skipped/nan `0/0`.
- Startup metric figure: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_balanced_v6/metrics/metric_curves_session80_iter130.png`.

## Verification

- Targeted tests: V6 M1 prep and Qwen scale-up planner tests passed.
- Pilot pipeline: local data prep, sync, remote train, metrics, checkpoint export, endpoint smoke, corrected MMLU-Pro eval, corrected AIME/HMMT eval.
- Full pipeline stage reached: uncapped data prep, Qwen tokenizer packing, train plan, remote sync, remote 8-GPU train launch, early iteration monitoring.
