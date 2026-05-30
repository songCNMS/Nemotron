# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task216 validated merged main commit
  `1d037329f5a02cdc04f2a09a16e7342721be4c87` with a task-owned checkout on
  NemTron.
- The task-owned config explicitly included
  `step_function: super3_packed_seq_compat_gpt_step`; the step registry probe
  resolved it to
  `nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`.
- Task215 changed `packed_compat_step.forward_step` so the first parameter is
  named `state`; the task216 probe confirmed the runtime signature as
  `(state, data_iterator, model=None, return_schedule_plan=False)`.
- The task216 traceback reached state-aware upstream Bridge
  `gpt_step.forward_step(state, data_iterator, compat_model, ...)`, so the
  previous task214 blocker
  `PACKED_COMPAT_STEP_BRIDGE_STATE_INJECTION_DETECTION` is no longer the
  active failure.
- New live blocker:
  `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`.
- The canonical run did not produce a checkpoint and left GPUs/ports clean after
  failure.
