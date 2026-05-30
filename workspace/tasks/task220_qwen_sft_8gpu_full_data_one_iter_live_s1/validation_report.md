# task220 Validation Report

Owner: `intern_nem_dev_2`

Branch: `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1`

Product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Artifact root:
`/mnt/cephfs/data/processing/nemotron-live-validation/task220`

## Result

PASS. Exactly one 8-GPU torchrun was launched and returned
`task220_torchrun_rc=0`.

## Command

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task220/Nemotron
PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task220/Nemotron/src \
NEMO_RUN_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1 \
SUPER3_M1_AGENTIC_PACKED_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full/splits \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE=/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/checkpoints_one_iter \
WANDB_DISABLED=true \
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
/usr/local/bin/torchrun --nproc_per_node=8 --master_addr=127.0.0.1 --master_port=29591 \
  src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py \
  --config /mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/m1_agentic_8gpu_full_qwen30b_contract.yaml \
  train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

## Preflight

- NemTron could not directly see the original task208 full split path, so full
  data was staged to:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full`.
- Preflight passed:
  - all 8 H200 visible
  - no H200 compute apps
  - no SGLang/task210 process
  - no `:13000` listener
  - selected master port `29591` free
  - `:8000` documented and untouched
- Data/config probe passed:
  - Qwen packed-data contract validated
  - `super3_packed_seq_compat_gpt_step` resolved to
    `nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`
  - train entrypoint resolved to
    `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
  - required imports resolved from the approved task218/task209 stack overlays

## Run Evidence

Torchrun log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/04_canonical_8gpu_one_iter_torchrun.log`

- `task220_torchrun_rc=0`
- Iteration: `1/1`
- Consumed samples: `8`
- Elapsed time per iteration: `36127.5 ms`
- Global batch size: `8`
- `lm loss: 1.226097E+01`
- `load_balancing_loss: 3.226302E+00`
- Grad norm: `123.805`
- Skipped iterations: `0`
- NaN iterations: `0`
- Validation loss at iteration 1: `1.043498E+01`
- Validation PPL: `3.402951E+04`

## Checkpoint

Checkpoint path:
`/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/checkpoints_one_iter`

- Size: `399G`
- Latest checkpointed iteration: `1`
- Iteration directory: `iter_0000001`
- Full inventory is in:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/05_checkpoint_cleanup_state.log`
- Small-file hash evidence includes
  `latest_checkpointed_iteration.txt`, `latest_train_state.pt`, `common.pt`,
  `metadata.json`, `modelopt_run_config.yaml`, `run_config.yaml`, and
  `train_state.pt`.

## Cleanup

Post-run cleanup log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/05_checkpoint_cleanup_state.log`

- No task220 torchrun/Qwen processes remained.
- No H200 compute apps remained.
- `:13000` clear.
- Master port `29591` clear.
- `:8000` documented-only listener remained untouched.

## Estimates And Risk

- Small pilot estimate, using this validated path with limited iterations and
  checkpoint cadence: about 1-3 hours of wall time depending on save/eval
  cadence and I/O.
- Full training estimate: about 12-36 wall-clock hours plus scheduling and
  checkpoint/export/eval windows, consistent with earlier 8-H200 Qwen SFT
  runs.
- Residual risk: this was a random-init one-iteration smoke because no
  pretrained Megatron checkpoint path was supplied. It validates the
  distributed runtime path, full packed data visibility, train step, validation,
  and checkpointing; it does not validate final model quality.
