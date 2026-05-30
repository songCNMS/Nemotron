# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Megatron-Bridge `prepare_forward_step_func` injects GlobalState only when a
  forward-step function exposes a compatible annotation or its first parameter
  is named `state` / `global_state`.
- The task213 adapter used first parameter `state_or_data_iterator`; Bridge did
  not inject state, so runtime schedule called `forward_step(data_iterator,
  model)` directly.
- With runtime state-aware upstream `gpt_step.forward_step(state,
  data_iterator, model, return_schedule_plan=False)`, the direct two-arg branch
  delegates incorrectly and reproduces the missing `model` TypeError.
- The adapter first parameter must be named `state`, and Bridge-injected runtime
  behavior should be modeled as `partial(forward_step, state)(data_iterator,
  model)`.
- Closeout note: PR #311 merged this fix into `main` at
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`; no new product behavior was
  added during closeout.
