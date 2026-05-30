# task219 Validation Report

Owner: `intern_nem_dev_2`

Branch: `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1`

Base / product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Artifact root:
`/mnt/cephfs/data/processing/nemotron-live-validation/task219`

## Status

- PM released task219 after task218 read-only verification passed.
- Task-owned code checkout/config/commit marker were staged under the task219
  artifact root.
- Exactly one canonical torchrun was launched.
- Result: PASS, `task219_torchrun_rc=0`.

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

## Read-Only Validation

NemTron pre-run read-only probe:

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

## Run Result

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs/03_canonical_one_iter_torchrun.log`

- `task219_torchrun_rc=0`.
- Iteration evidence:
  - iteration `1/1`
  - consumed samples `1`
  - elapsed time per iteration `60567.7 ms`
  - `lm loss: 1.195105E+01`
  - loss scale `1.0`
  - grad norm `5.380`
  - skipped iterations `0`
  - nan iterations `0`
- Checkpoint save evidence:
  - `successfully saved checkpoint from iteration 1`
  - path:
    `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`

## Checkpoint And Cleanup

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs/04_checkpoint_gpu_state_after_run.log`

- NemTron checkpoint path exists:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`
- NemTron checkpoint size: `1.2G`.
- Iteration directory:
  `iter_0000001`.
- Key checkpoint files and sizes:
  - `.metadata`: `259415`
  - `__0_0.distcp`: `635451007`
  - `__0_1.distcp`: `635468477`
  - `common.pt`: `2093`
  - `metadata.json`: `119`
  - `run_config.yaml`: `18539`
  - `train_state.pt`: `3405`
  - `latest_checkpointed_iteration.txt`: `1`
  - `latest_train_state.pt`: `3405`
- Key checkpoint hashes:
  - `__0_0.distcp`:
    `c6a6a720273024cb3218f639415b9afbe56fbf2003e478fa27a5ed0b775750e8`
  - `__0_1.distcp`:
    `586ed3dee7a6ecc90a9c4d39af5c73c8dac9257ce4108daa591678fc5c43d10a`
  - `run_config.yaml`:
    `b3ae2369ff7a7bfa6987344bf2e06da3da0be429dc03c5ae9cdc7c6c5e0f5d25`
  - `train_state.pt`:
    `d0c54a05fd6b45c143335f2794923541871f64da79935743462f26111c27d054`
  - `latest_checkpointed_iteration.txt`:
    `6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b`
- Full checkpoint inventory and sha256 list are in the checkpoint cleanup log.
- Post-run cleanup: no H200 compute apps, `:13000` clear, `:29581` clear, and
  `:8000` documented-only/untouched.

## Local-Visible Artifacts

Manifest:
`/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs/05_local_visibility_copy_manifest.log`

- Copied local-visible logs/config/commit marker:
  - `00_local_setup.log`
  - `00_remote_code_stage.log`
  - `01_data_stack_step_probe.log`
  - `02_preflight_port_gpu.log`
  - `03_canonical_one_iter_torchrun.log`
  - `04_checkpoint_gpu_state_after_run.log`
  - `05_local_visibility_copy_manifest.log`
  - `m1_agentic_smoke_qwen_contract.yaml`
  - `.task219_commit`
- Local CPU checkpoint visibility:
  `checkpoint_local_visibility=MISSING`.
- The checkpoint exists on NemTron and the checkpoint evidence log is
  local-visible.

## Data Hashes

- `blend.json`:
  `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
- `splits/metadata.json`:
  `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
- `splits/packed_4096_metadata.json`:
  `e3ddef75fffa658bc5317b2240d8c87863837629bd016bb68c311d2feabb983b`
- `splits/train/shard_000000.parquet`:
  `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`

## Blockers

- None for the one-iteration task219 smoke.
- No second launch or workaround was attempted.
