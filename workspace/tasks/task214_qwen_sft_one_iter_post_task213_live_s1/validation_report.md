# task214 Validation Report

Owner: `intern_nem_dev_2`

Branch: `intern_nem_dev_2/task214_qwen_sft_one_iter_post_task213_live_s1`

Base / product commit: `4fe9454e46343821f68e43c47cdeba1aaf0fef84`

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task214`

## Inputs

- Code checkout:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron`
- Commit marker:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron/.task214_commit`
- Config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/m1_agentic_smoke_qwen_contract.yaml`
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
`/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/logs/01_data_stack_step_probe.log`

- `step_function=super3_packed_seq_compat_gpt_step`.
- Registry target:
  `nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`.
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
`/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/logs/02_preflight_port_gpu.log`

- No SGLang/task210 process.
- No `:13000` listener.
- No H200 compute apps.
- Chosen torchrun master port: `29561`, free before launch.
- `:8000` documented-only listener, untouched.

## Command

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron/src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29561 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

## Result

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/logs/03_canonical_one_iter_torchrun.log`

- Result: FAIL, `task214_torchrun_rc=1`.
- Reached stage: distributed init, tokenizer/model/optimizer/dataloader setup,
  and training loop start at iteration 0.
- Traceback:

```text
File ".../megatron/core/pipeline_parallel/schedules.py", line 417, in forward_step
  output_tensor, loss_func = forward_step_func(data_iterator, model)
File ".../src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py", line 157, in forward_step
  return upstream_forward_step(data_iterator, compat_model)
TypeError: forward_step() missing 1 required positional argument: 'model'
```

Blocker:
`PACKED_COMPAT_STEP_BRIDGE_STATE_INJECTION_DETECTION`.

PM read-only log/root-cause note: Bridge `prepare_forward_step_func` only
injects `GlobalState` when the forward-step first parameter is named `state` /
`global_state` or annotated as `GlobalState`; the adapter first parameter is
`state_or_data_iterator`, so Bridge did not inject state. The schedule called
`adapter(data_iterator, model)`, and the adapter's two-argument branch delegated
to state-aware upstream Bridge `gpt_step` without the required state argument.

## Checkpoint And Cleanup

Log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/logs/04_checkpoint_gpu_state_after_run.log`

- Checkpoint path missing:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/checkpoints_one_iter`.
- No H200 compute apps after run.
- `:13000` clear.
- `:29561` clear.
- `:8000` documented-only listener still present and untouched.

## Local-Visible Artifacts

Manifest:
`/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/logs/05_local_visibility_copy_manifest.log`

Copied locally visible artifacts include:

- `00_local_setup.log`
- `00_remote_code_stage.log`
- `01_data_stack_step_probe.log`
- `02_preflight_port_gpu.log`
- `03_canonical_one_iter_torchrun.log`
- `04_checkpoint_gpu_state_after_run.log`
- `05_local_visibility_copy_manifest.log`
- `m1_agentic_smoke_qwen_contract.yaml`
- `.task214_commit`

## Estimates

- Small pilot/full train were not launched per task boundary.
- Because the one-iteration canonical smoke fails before completing iteration 1,
  the current estimate for small/full training is blocked until
  `PACKED_COMPAT_STEP_BRIDGE_STATE_INJECTION_DETECTION` is fixed and a
  one-iteration smoke passes.
