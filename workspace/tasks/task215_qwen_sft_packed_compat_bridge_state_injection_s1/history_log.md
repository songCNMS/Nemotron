# History Log

<!-- METADATA:SESSION=2 -->

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

## Session 2 - 2026-05-30

- Received PM closeout assignment after PR #311 merged. Tested/merged PR head
  was `3538f89b3885cc5f9f8c0523f83d144ad55daac8`; merged main is
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Synced local `main` to exact `origin/main`
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Created closeout branch
  `intern_nem_dev_1/task215_closeout_status_s2` for status/task docs only.
- Set dev status to Idle / Current Task None and recorded task215 closeout.
- No product code edits, live train, endpoint, benchmark, package install,
  W&B/cluster/deploy, artifact upload, direct `main`/`master` push, or
  self-merge were run.
