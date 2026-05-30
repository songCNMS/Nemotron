# Task Knowledge

<!-- METADATA:SESSION=3 -->

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
- PR #310 merged to `main` as
  `4fe9454e46343821f68e43c47cdeba1aaf0fef84` after gate on final head
  `d441af6bd9450ba79400a234debb625712da9de7`.
