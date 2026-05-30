# task212 Validation Report

<!-- METADATA:SESSION=3 -->

## Summary

Task212 reran the canonical one-GPU Qwen-contract Stage1 SFT one-iteration
smoke on NemTron after task211 / PR #309 merged. The run used fixed code from
exact commit `f65dafdb15b28342c1fbd4a5ead807052bcdd264` staged under the
task212 artifact root.

Result: FAIL, `task212_torchrun_rc=1`.

PM accepted this single run as task212 evidence because the task-owned config
did include `step_function: super3_packed_seq_compat_gpt_step` and the traceback
entered `packed_compat_step.py`. No rerun or workaround was attempted.

The run reached the training loop, then failed in the new packed sequence
compatibility adapter:

```text
TypeError: forward_step() missing 1 required positional argument: 'model'
```

## Artifact Paths

- Task root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212`
- Session root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1`
- Fixed-code snapshot:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/Nemotron`
- Qwen contract config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/m1_agentic_smoke_qwen_contract.yaml`
- Checkpoint target:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/checkpoints_one_iter`

## Logs

- Local setup:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/00_local_setup.log`
- Remote code staging:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/00_remote_code_stage.log`
- Data and train-stack probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/01_data_and_train_stack_probe.log`
- Preflight:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/02_preflight_port_gpu.log`
- Canonical torchrun:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/03_canonical_one_iter_torchrun.log`
- Post-run checkpoint/GPU/port state:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/04_checkpoint_gpu_state_after_run.log`
- Local-visible copy manifest:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/05_local_visibility_copy_manifest.log`
- Post-addendum step-function resolution probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/06_step_function_resolution_probe_after_launch.log`
- Post-addendum local-visible copy manifest:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/07_local_visibility_post_addendum_manifest.log`

## Inputs

Code commit:

`f65dafdb15b28342c1fbd4a5ead807052bcdd264`

Train stack:

- `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`

Packed data:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`

Recorded hashes:

- `blend.json`:
  `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
- `splits/metadata.json`:
  `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
- `splits/packed_4096_metadata.json`:
  `e3ddef75fffa658bc5317b2240d8c87863837629bd016bb68c311d2feabb983b`
- `splits/train/shard_000000.parquet`:
  `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`

Model/tokenizer:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

## Preflight

Preflight passed:

- no SGLang/task210 process
- no `:13000` listener
- no H200 compute apps
- all eight H200s idle at about 1 MiB used and 0% utilization
- selected free torchrun master port `29541`
- `:8000` still listening on `0.0.0.0:8000`; documented and left untouched

## Command

Exactly one canonical run was launched:

```bash
ssh -o BatchMode=yes NemTron 'cd "/mnt/cephfs/data/processing/nemotron-live-validation/task212/Nemotron" && \
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task212/Nemotron/src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29541 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 \
  checkpoint.save_interval=1 \
  artifacts.wandb=false \
  artifacts.manifest.root=null'
```

The command used a task-owned copied config that explicitly includes:

```yaml
step_function: super3_packed_seq_compat_gpt_step
```

## Result

`task212_torchrun_rc=1`

The run passed the previous missing-package blockers and the previous direct
`packed_seq_params` Mamba forward error was not reproduced directly. It reached:

- distributed initialization
- Qwen tokenizer build
- hybrid Mamba/MoE tiny model build
- optimizer/scheduler setup
- packed-data iterator setup
- training loop start at iteration 0

Failure:

```text
File ".../src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py", line 143, in forward_step
  return upstream_forward_step(data_iterator, compat_model)
TypeError: forward_step() missing 1 required positional argument: 'model'
```

Current blocker: `PACKED_COMPAT_STEP_UPSTREAM_FORWARD_ARITY`.

Exact arity mismatch: current Megatron Bridge `gpt_step.forward_step` expects
`(state, data_iterator, model, return_schedule_plan=False)`, while the task211
adapter called it with `(data_iterator, compat_model)`.

## Step-Function Addendum Evidence

PM's addendum requiring explicit step-function proof arrived after the single
task212 torchrun had already completed. I did not launch a second run.

Post-addendum probe result:

```text
step_function=super3_packed_seq_compat_gpt_step
registry_target=nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step
resolved_module=nemotron.recipes.super3.stage1_sft.packed_compat_step
resolved_name=forward_step
step_function_probe_rc=0
```

The same probe grepped the completed torchrun log and confirmed the traceback
entered `packed_compat_step.py` before the arity failure:

```text
packed_compat_step.py\", line 143, in forward_step
TypeError: forward_step() missing 1 required positional argument: 'model'
task212_torchrun_rc=1
```

## Checkpoint And Cleanup State

- Checkpoint target is missing:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/checkpoints_one_iter`
- No H200 compute apps after the run.
- All eight H200s idle after the run.
- `:13000` clear after the run.
- `:29541` clear after the run.
- `:8000` remained listening and untouched.

## Estimates

- Small pilot: blocked until the compat-step arity issue is fixed and a
  successful one-iteration smoke produces step-time evidence.
- Full train: still blocked. Existing task208 full packing metrics from task209
  remain `987770` packed sequences and `672687706` tokens across 16 shards.
  With `global_batch_size=1`, one full pass would require `987770` optimizer
  iterations; wall-clock estimate cannot be made from this failed run because it
  did not complete one iteration.

## Session 3 PM Acceptance

PM accepted the single run as final task212 evidence. The late addendum arrived
after the run and did not require a rerun because the task-owned copied config
already included `step_function: super3_packed_seq_compat_gpt_step`; the
post-addendum probe confirmed registry resolution to
`nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`.

No further live train, train workaround, package install, system mutation,
process kill, endpoint, benchmark/eval, W&B, cluster/deploy, artifact upload,
full train, or multi-GPU train was performed.
