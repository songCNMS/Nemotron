# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Runtime Megatron-Bridge `gpt_step.forward_step` in the task212 environment
  has signature `(state, data_iterator, model, return_schedule_plan=False)`.
- The task211 adapter failed because it only called upstream
  `forward_step(data_iterator, compat_model)`, producing
  `TypeError: forward_step() missing 1 required positional argument: 'model'`.
- `packed_compat_step.forward_step` must wrap only the model argument with
  `_drop_unsupported_packed_seq_params`; `state`, `data_iterator`, and
  `return_schedule_plan` must pass through unchanged.
- The local two-argument test stub path is still useful because it keeps
  sandbox tests independent of an installed Megatron-Bridge runtime.
