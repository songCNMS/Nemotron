# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task214 validated merged main commit
  `4fe9454e46343821f68e43c47cdeba1aaf0fef84` with a task-owned checkout on
  NemTron.
- The task-owned config explicitly included
  `step_function: super3_packed_seq_compat_gpt_step`; the step registry probe
  resolved it to
  `nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`.
- The task214 runtime entered `packed_compat_step.py`, so the run exercised the
  intended compatibility adapter rather than the default `gpt_step`.
- In this runtime, Megatron Core schedule
  `megatron/core/pipeline_parallel/schedules.py` called
  `forward_step_func(data_iterator, model)`.
- The adapter's two-argument branch still calls Bridge upstream as
  `upstream_forward_step(data_iterator, compat_model)`, but installed
  Megatron Bridge `gpt_step.forward_step` expects a state-aware call shape with
  at least `(state, data_iterator, model)`.
- New live blocker:
  `PACKED_COMPAT_STEP_BRIDGE_STATE_INJECTION_DETECTION`.
- PM read-only log inspection identified the detection root cause: Bridge
  `prepare_forward_step_func` only injects `GlobalState` when the forward-step
  first parameter is named `state` / `global_state` or annotated as
  `GlobalState`; `state_or_data_iterator` was not detected, so no state was
  injected.
- The canonical run did not produce a checkpoint and left GPUs/ports clean after
  failure.
