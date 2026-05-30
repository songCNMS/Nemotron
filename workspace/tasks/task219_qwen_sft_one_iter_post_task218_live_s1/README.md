# task219_qwen_sft_one_iter_post_task218_live_s1

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Scope

- Qwen-contract Stage1 SFT one-iteration smoke after task218 causal-conv1d
  train-stack work was accepted by PM.
- PM released the single canonical run after task218 read-only verification
  passed.
- Base / product commit remains
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Prepared branch:
  `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1`.
- Intended artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219`.

## Boundaries

- Exactly one canonical torchrun only.
- No process kill, package install/build, endpoint, eval, benchmark, model copy,
  system mutation, full or multi-GPU train, W&B, cluster, deploy, artifact
  upload, direct `main`/`master` push, or self-merge.

## Prepared Inputs

- Baseline code commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Intended task-owned code checkout:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron`.
- Intended config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/m1_agentic_smoke_qwen_contract.yaml`.
- Packed data:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- PYTHONPATH order for the later run:
  1. `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target`
  2. `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`
  3. `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages`
  4. `/mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron/src`

## Read-Only Probe

Pre-run read-only probe on NemTron:

- Confirmed task218 `pip_target`, task209 Mamba target, task209 venv
  site-packages, task208 staged sample splits, and Qwen model path exist.
- Confirmed sample data hashes match task216:
  - `blend.json`:
    `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
  - `splits/metadata.json`:
    `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
  - `splits/packed_4096_metadata.json`:
    `e3ddef75fffa658bc5317b2240d8c87863837629bd016bb68c311d2feabb983b`
  - `splits/train/shard_000000.parquet`:
    `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`
- With the prepared PYTHONPATH prefix, `causal_conv1d`,
  `causal_conv1d_cuda`, `mamba_ssm`, `torch`, `megatron.bridge`,
  `megatron.energon`, and `nemo_run` are import-visible.
- `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_fwd_function` resolved to a
  function object, not `None`.
- Preflight found no SGLang/task210 process, no `:13000` listener, no H200
  compute apps, free candidate master port `29581`, and `:8000`
  documented/untouched.

## Command

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

## Result

- PASS: `task219_torchrun_rc=0`.
- Reached iteration `1/1` with `lm loss: 1.195105E+01`, grad norm `5.380`,
  skipped iterations `0`, and nan iterations `0`.
- Saved checkpoint at iteration 1 under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`.
- NemTron checkpoint size: `1.2G`.
- Post-run cleanup passed: no H200 compute apps, `:13000` clear, `:29581`
  clear, and `:8000` documented-only/untouched.
- Local-visible manifest notes the checkpoint directory itself is not visible
  from the local CPU namespace; checkpoint inventory and sha256 evidence are in
  local-visible log
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs/04_checkpoint_gpu_state_after_run.log`.

## Blockers

- None for the one-iteration task219 smoke.
- No second run or workaround was attempted.
