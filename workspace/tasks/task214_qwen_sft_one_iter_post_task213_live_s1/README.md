# task214_qwen_sft_one_iter_post_task213_live_s1

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nem_dev_2,SESSION=2 -->

## Scope

- Evidence-only live validation after task213 / PR #310.
- Rerun exactly one canonical single-GPU Qwen-contract Stage1 SFT
  one-iteration smoke on NemTron at merged main commit
  `4fe9454e46343821f68e43c47cdeba1aaf0fef84`.
- Use a task-owned fixed-code checkout and a config that explicitly sets
  `step_function: super3_packed_seq_compat_gpt_step`.
- Reuse the task209 train stack and task208 sample packed data staged under
  task209.

## Boundaries

- No second train launch or workaround after the single canonical run.
- No full or multi-GPU training, eval, benchmark, endpoint, W&B, cluster,
  deploy, artifact upload, system/package mutation, direct `main`/`master`
  push, or self-merge.

## Status

- Branch: `intern_nem_dev_2/task214_qwen_sft_one_iter_post_task213_live_s1`.
- Base / code commit: `4fe9454e46343821f68e43c47cdeba1aaf0fef84`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214`.
- Task-owned code checkout:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron`.
- Commit marker:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron/.task214_commit`.
- Task-owned config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/m1_agentic_smoke_qwen_contract.yaml`.
- Packed data:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Qwen model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Result

- Preflight passed: no SGLang/task210 process, no `:13000` listener, no H200
  compute apps, and torchrun master port `29561` was free.
- `:8000` remained a documented-only listener and was not touched.
- Exactly one canonical single-GPU torchrun was launched with
  `CUDA_VISIBLE_DEVICES=0`, `train.train_iters=1`,
  `checkpoint.save_interval=1`, W&B disabled, and manifest root null.
- The run reached distributed init, tokenizer/model/optimizer/dataloader setup,
  and the training loop at iteration 0.
- The run failed with `task214_torchrun_rc=1`:
  `TypeError: forward_step() missing 1 required positional argument: 'model'`.
- Checkpoint state: missing
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/session1/checkpoints_one_iter`.
- Post-run cleanup passed: no H200 compute apps, `:13000` and `:29561` clear,
  and `:8000` still documented-only.

## Blocker

`PACKED_COMPAT_STEP_BRIDGE_STATE_INJECTION_DETECTION`: the task213 fixed
adapter is registered and used, but Bridge did not inject `GlobalState` into the
adapter. PM root-cause note: `prepare_forward_step_func` only injects
`GlobalState` when the forward-step first parameter is named `state` /
`global_state` or annotated as `GlobalState`; the current adapter first
parameter is `state_or_data_iterator`, so the active schedule called
`adapter(data_iterator, model)`. The two-argument branch then delegated to the
state-aware upstream Bridge `gpt_step` without a state argument and failed with
`TypeError: forward_step() missing 1 required positional argument: 'model'`.

No workaround or second launch was attempted.
