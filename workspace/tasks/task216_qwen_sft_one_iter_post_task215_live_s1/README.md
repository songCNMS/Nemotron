# task216_qwen_sft_one_iter_post_task215_live_s1

<!-- METADATA:STATUS=Idle,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Scope

- Evidence-only live validation after task215 / PR #311.
- Run exactly one canonical single-GPU Qwen-contract Stage1 SFT one-iteration
  smoke on NemTron at merged main commit
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Use a task-owned fixed-code checkout and a config that explicitly sets
  `step_function: super3_packed_seq_compat_gpt_step`.
- Reuse the task209 train stack and task208 sample packed data staged under
  task209.

## Boundaries

- Exactly one canonical torchrun only.
- No second train launch or workaround after the canonical run.
- No full or multi-GPU training, eval, benchmark, endpoint, W&B, cluster,
  deploy, artifact upload, system/package mutation, direct `main`/`master`
  push, or self-merge.

## Status

- Branch: `intern_nem_dev_2/task216_qwen_sft_one_iter_post_task215_live_s1`.
- Base / code commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216`.
- Task-owned code checkout:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron`.
- Commit marker:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/.task216_commit`.
- Task-owned config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/m1_agentic_smoke_qwen_contract.yaml`.
- Packed data:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Qwen model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Result

- Preflight passed: no SGLang/task210 process, no `:13000` listener, no H200
  compute apps, and torchrun master port `29571` was free.
- `:8000` remained a documented-only listener and was not touched.
- Exactly one canonical single-GPU torchrun was launched with
  `CUDA_VISIBLE_DEVICES=0`, `train.train_iters=1`,
  `checkpoint.save_interval=1`, W&B disabled, and manifest root null.
- The run reached distributed init, tokenizer/model/optimizer/dataloader setup,
  and the training loop at iteration 0.
- The task215 state-injection fix was exercised: the traceback reached
  state-aware upstream Bridge `gpt_step.forward_step` and then model forward,
  not the previous missing-`model` error.
- The run failed with `task216_torchrun_rc=1`:
  `TypeError: 'NoneType' object is not callable` from
  `mamba_ssm/ops/triton/ssd_combined.py` while calling
  `causal_conv1d_fwd_function(...)`.
- Checkpoint state: missing
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/checkpoints_one_iter`.
- Post-run cleanup passed: no H200 compute apps, `:13000` and `:29571` clear,
  and `:8000` still documented-only.

## Blocker

`MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`: after task215 fixed Bridge state
injection, the one-iteration smoke progressed into Mamba model forward and
failed because the task209 session5 `mamba_ssm` target has
`causal_conv1d_fwd_function` as `None`.

No workaround or second launch was attempted.
