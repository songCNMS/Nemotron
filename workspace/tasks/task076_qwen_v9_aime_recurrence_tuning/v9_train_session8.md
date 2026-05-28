# V9 Training Session 8

Date: 2026-05-28
Executor: intern_nemontron_code_reading

## Objective

Launch the V9 Qwen3-30B-A3B recurrence/counting tuning run from V8 `iter_0000779` using the Session 7 packed data and training plan.

## Inputs

- Local output bundle: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9`
- Remote run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9`
- Packed data: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/packed_qwen/splits`
- Training manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/training_plan/task076_qwen30b_a3b_hard_math_recurrence_v9/training_manifest.json`
- Starting checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`
- Qwen HF metadata/tokenizer path: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

## Remote Qwen Path Handling

The user requested the Qwen model/checkpoint path be switched to `/mnt/cephfs/data/stable/models/Qwen`. The exact local model directory used by the V9 plan is:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

On NemTron, `/mnt/cephfs` was not mounted. To keep the generated path stable, Session 8 created a lightweight metadata/tokenizer mirror at the same path and copied all files except `model-*.safetensors`.

Preflight passed:

- `tokenizer_config.json`, `tokenizer.json`, `vocab.json`, `merges.txt`, `config.json`, `generation_config.json`, and `model.safetensors.index.json` were present.
- `_qwen30b_a3b_local_recipe_builder` built the Qwen 30B-A3B config successfully with `seq_length=8192`, `tp=4`, `pp=2`, `ep=4`, and tokenizer path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- This is sufficient because Megatron-Bridge uses `AutoBridge.from_hf_pretrained(...).to_megatron_provider(load_weights=False)` for the HF path, while train weights load from the V8 NeMo checkpoint.

## Commands

Sync:

```bash
/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/sync_to_nemtron.sh
```

Launch:

```bash
/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_nemtron_train.sh
```

Remote tmux session:

`task067_task076_qwen30b_a3b_hard_math_recurrence_v9`

Train log:

`/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/logs/train.log`

## Training Result

- GPUs: 8x H200
- Train entrypoint: `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- Planned iterations: `192`
- Completed iterations: `192`
- Global batch size: `8`
- Micro batch size: `1`
- Sequence length: `8192`
- LR: `8e-8`
- Min LR: `3e-8`
- Warmup iters: `20`

Observed train health:

- Iter 10 train lm loss: `12.25112`
- Iter 50 train lm loss: `11.19961`
- Iter 100 train lm loss: `9.722968`
- Iter 100 validation loss: `9.630936`
- Iter 150 train lm loss: `9.152428`
- Iter 190 train lm loss: `8.950349`
- Final iter 192 validation loss: `8.960094`

No traceback, OOM, runtime error, or missing-path failure was observed in the monitored log.

## Checkpoints

Saved checkpoints:

- `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000100`
- `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000192`

Final checkpoint files include distributed checkpoint shards, tokenizer files, `run_config.yaml`, `modelopt_run_config.yaml`, `train_state.pt`, `common.pt`, and `metadata.json`.

## Next Step

Run the targeted recurrence/counting smoke on V9 `iter_0000192`, starting with `aime_06`-style prompts, before exporting/running the full corrected MMLU-Pro/AIME25/HMMT gate.
