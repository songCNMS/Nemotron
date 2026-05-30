# task219 Prepare-Only Report

Owner: `intern_nem_dev_2`

Branch: `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1`

Base / product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Artifact root for future release:
`/mnt/cephfs/data/processing/nemotron-live-validation/task219`

## Status

- Prepare-only branch/docs/report skeleton completed.
- No torchrun/train launch was run.
- No task-owned code checkout/config was staged under task219 yet.
- Hold reason: waiting for PM release after task218 exact-head read-only PASS.

## Prepared Command

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron/src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29581 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

## Read-Only Validation

NemTron read-only probe:

- Existing paths:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`
  - `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Imports visible with prepared PYTHONPATH prefix:
  `causal_conv1d`, `causal_conv1d_cuda`, `mamba_ssm`, `torch`,
  `megatron.bridge`, `megatron.energon`, and `nemo_run`.
- `ssd_combined.causal_conv1d_fwd_function` resolved as a function object:
  `<function causal_conv1d_fwd_function ...>`.
- `ssd_combined.causal_conv1d_fwd_function_is_none=false`.
- No SGLang/task210 process.
- No `:13000` listener.
- No H200 compute apps.
- Candidate master port `29581` free.
- `:8000` documented-only listener present and untouched.

## Data Hashes

- `blend.json`:
  `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
- `splits/metadata.json`:
  `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
- `splits/packed_4096_metadata.json`:
  `e3ddef75fffa658bc5317b2240d8c87863837629bd016bb68c311d2feabb983b`
- `splits/train/shard_000000.parquet`:
  `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`

## Release Checklist

Before any PM-released live run:

- Sync or confirm product commit/base requested by PM.
- Stage task-owned code checkout under task219 and write `.task219_commit`.
- Create task-owned config with
  `step_function: super3_packed_seq_compat_gpt_step` and the Qwen train
  entrypoint.
- Re-run no-SGLang/no-`:13000`/no-H200-compute/free-port preflight.
- Launch exactly one canonical torchrun only if PM explicitly releases it.
