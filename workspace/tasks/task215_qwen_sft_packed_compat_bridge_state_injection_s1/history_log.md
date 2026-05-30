# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-30

- Accepted PM task215 on branch
  `intern_nem_dev_1/task215_qwen_sft_packed_compat_bridge_state_injection_s1`
  from base `4fe9454e46343821f68e43c47cdeba1aaf0fef84`.
- Root cause from task214 evidence: the adapter first parameter was named
  `state_or_data_iterator`, so Megatron-Bridge `prepare_forward_step_func`
  did not inject GlobalState. Megatron-Core then called the adapter as
  `(data_iterator, model)`, causing the adapter to take its direct two-arg
  branch and call state-aware upstream `gpt_step` without `state`.
- Renamed the first adapter parameter to `state` and documented why that name
  is required for Bridge state-injection detection.
- Updated focused tests to simulate the Bridge-injected partial call shape,
  while preserving direct two-argument local stub coverage.
- Ran focused packed compat/dispatch pytest, Qwen selector pytest, broader
  SFT/Qwen validator shard, py_compile, Ruff, structured Bridge
  state-injection / no-live-surface probe, and `git diff --check`. No live
  training or forbidden operations were run.
- Opened PR #311 to `main` at implementation head
  `51fc113044039887410c8a4ff9da807940fc41ac`; GitHub reports merge state
  `CLEAN`.
