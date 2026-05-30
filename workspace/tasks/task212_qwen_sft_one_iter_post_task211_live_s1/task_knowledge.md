# Task Knowledge

<!-- METADATA:SESSION=3 -->

- Validated main / code commit:
  `f65dafdb15b28342c1fbd4a5ead807052bcdd264`.
- Branch:
  `intern_nem_dev_2/task212_qwen_sft_one_iter_post_task211_live_s1`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212`.
- Fixed-code NemTron snapshot:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/Nemotron`
  with `.task212_commit` containing
  `f65dafdb15b28342c1fbd4a5ead807052bcdd264`.
- Task-owned Qwen smoke config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/m1_agentic_smoke_qwen_contract.yaml`.
- Reused train-stack resources:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`.
- Reused sample packed splits:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Qwen model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Preflight master port selected: `29541`.
- `:8000` remains documented-only and must not be killed.
- Run result: `task212_torchrun_rc=1`; current blocker is
  `PACKED_COMPAT_STEP_UPSTREAM_FORWARD_ARITY`.
- PM accepted the single task212 run as evidence after reviewing logs. No rerun
  is needed because the task-owned config already used
  `step_function: super3_packed_seq_compat_gpt_step` and the traceback entered
  `packed_compat_step.py`.
- Exact arity mismatch: current Megatron Bridge `gpt_step.forward_step` expects
  `(state, data_iterator, model, return_schedule_plan=False)`, while the task211
  adapter called it with `(data_iterator, compat_model)`.
- PM addendum note: the addendum requiring explicit
  `step_function=super3_packed_seq_compat_gpt_step` evidence arrived after the
  single task212 live run had already completed. No second run was launched.
- The task212 run used a task-owned copied config that explicitly declares
  `step_function: super3_packed_seq_compat_gpt_step`; it did not use the raw
  upstream `m1_agentic_smoke.yaml`.
- Step-function probe log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/logs/06_step_function_resolution_probe_after_launch.log`.
  It confirms `_STEP_FUNCTIONS["super3_packed_seq_compat_gpt_step"] ==
  "nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step"` and
  `_load_forward_step()` resolves to `packed_compat_step.forward_step`.
- Failure signature:
  `TypeError: forward_step() missing 1 required positional argument: 'model'`
  from
  `src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py`.
- The previous task209 `MambaModel.forward(... packed_seq_params)` error was
  not reproduced directly; the post-task211 code now reaches the compat adapter
  and fails there before completing the first iteration.
- Checkpoint path
  `/mnt/cephfs/data/processing/nemotron-live-validation/task212/session1/checkpoints_one_iter`
  is missing because the run failed before checkpoint save.
- Full/small train remains blocked until the compat-step arity issue is fixed.
