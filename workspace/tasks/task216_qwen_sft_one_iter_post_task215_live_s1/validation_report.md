# task216 Validation Report

Owner: `intern_nem_dev_2`

Branch: `intern_nem_dev_2/task216_qwen_sft_one_iter_post_task215_live_s1`

Base / product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task216`

## Inputs

- Code checkout:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron`
- Commit marker:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/.task216_commit`
- Config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/m1_agentic_smoke_qwen_contract.yaml`
- Packed data:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Train stack:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`

## Data And Config Evidence

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/01_data_stack_step_probe.log`

- `step_function=super3_packed_seq_compat_gpt_step`.
- Registry target:
  `nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`.
- Adapter first parameter: `state`.
- Adapter signature:
  `(state: 'Any', data_iterator: 'Any', model: 'Any | None' = None, return_schedule_plan: 'bool' = False)`.
- Data hashes:
  - `blend.json`:
    `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
  - `splits/metadata.json`:
    `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
  - `splits/packed_4096_metadata.json`:
    `e3ddef75fffa658bc5317b2240d8c87863837629bd016bb68c311d2feabb983b`
  - `splits/train/shard_000000.parquet`:
    `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`

## Preflight

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/02_preflight_port_gpu.log`

- No SGLang/task210 process.
- No `:13000` listener.
- No H200 compute apps.
- Chosen torchrun master port: `29571`, free before launch.
- `:8000` documented-only listener, untouched.

## Command

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29571 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

## Result

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/03_canonical_one_iter_torchrun.log`

- Result: FAIL, `task216_torchrun_rc=1`.
- Reached stage: distributed init, tokenizer/model/optimizer/dataloader setup,
  and training loop start at iteration 0.
- Task215 runtime confirmation: the previous missing-`model` arity failure did
  not recur; traceback reached upstream Bridge `gpt_step.forward_step` and
  Mamba model forward.
- No loss value was emitted because the step failed during forward before the
  first iteration completed.
- Traceback:

```text
File ".../packed_compat_step.py", line 162, in forward_step
  return upstream_forward_step(
File ".../megatron/bridge/training/gpt_step.py", line 209, in forward_step
  output, loss_mask = _forward_step_common(state, data_iterator, model, return_schedule_plan)
File ".../mamba_ssm/ops/triton/ssd_combined.py", line 996, in mamba_split_conv1d_scan_combined
  return MambaSplitConv1dScanCombinedFn.apply(...)
File ".../mamba_ssm/ops/triton/ssd_combined.py", line 840, in forward
  causal_conv1d_fwd_function(...)
TypeError: 'NoneType' object is not callable
```

Blocker:
`MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`.

## Checkpoint And Cleanup

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/04_checkpoint_gpu_state_after_run.log`

- Checkpoint path missing:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/checkpoints_one_iter`.
- No H200 compute apps after run.
- `:13000` clear.
- `:29571` clear.
- `:8000` documented-only listener still present and untouched.

## Local-Visible Artifacts

Manifest:
`/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/05_local_visibility_copy_manifest.log`

Copied locally visible artifacts include:

- `00_local_setup.log`
- `00_remote_code_stage.log`
- `01_data_stack_step_probe.log`
- `02_preflight_port_gpu.log`
- `03_canonical_one_iter_torchrun.log`
- `04_checkpoint_gpu_state_after_run.log`
- `05_local_visibility_copy_manifest.log`
- `m1_agentic_smoke_qwen_contract.yaml`
- `.task216_commit`

## Estimates

- Small pilot/full train were not launched per task boundary.
- Because the one-iteration canonical smoke fails before completing iteration 1,
  the current estimate for small/full training is blocked until
  `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE` is resolved and a one-iteration
  smoke passes.
