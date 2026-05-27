# Qwen 30B-A3B V8 Train Session 94

## Scope

Run the V8 full local data-prep path, inspect hard-row scale, sync to NemTron, and execute a bounded 30B-A3B train-to-validation run.

## Data Scale

- Strategy: `hard_math_clean_final_v8`
- Base M1 train rows: `983397`
- Val-shadow rows: `11354`
- V8 hard clean final rows: `4546/4546`
- Errors: `0`
- Packed sequences: `987770`
- Packed tokens: `672788411`
- Pack/sequence length: `8192/8192`
- Packed train/valid rows: `31144/2546`
- Train shards: `32`
- Valid shards: `1`
- Planned train iters: `779`

## Training

- Remote path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8`
- Entrypoint: `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- GPUs: `8` H200
- GBS/MBS: `8/1`
- LR/min LR: `2e-7/8e-8`
- Warmup iters: `100`
- Eval/save interval: `400`
- Final checkpoint: `checkpoints/iter_0000779`
- Intermediate checkpoint: `checkpoints/iter_0000400`

## Metrics

- Iter `400`: train lm loss `0.4720876`; validation loss/PPL `0.4647015/1.591539`
- Iter `779`: validation loss/PPL `0.4463005/1.562521`
- Latest parsed train point: iter `770`, train lm loss `0.4295896`, LR `8.005201e-08`, grad norm `0.597`
- Max skipped/nan iterations: `0/0`
- Validation trend: improved from iter `400` to final iter `779`

## Artifacts

- Local output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8`
- Remote train log copied to: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/metrics/train.log`
- Metric curve: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/metrics/metric_curves_session94_final_iter779.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/metrics/health_summary.json`

## Handoff

- Export `iter_0000779` to HF using the established Megatron-Bridge export path.
- Serve the export with SGLang `tp=4`, `dp=2`, `context_length=16384`.
- Run corrected full eval with the same gates used for V7: MMLU-Pro full, AIME25 `max_tokens=8192`, and HMMT `max_tokens=8192`.
