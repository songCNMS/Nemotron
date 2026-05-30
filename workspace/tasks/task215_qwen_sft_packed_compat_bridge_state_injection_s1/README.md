# task215_qwen_sft_packed_compat_bridge_state_injection_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Fix the task214 rerun failure where merged task213 still reached
  `packed_compat_step.py` and delegated to state-aware upstream `gpt_step`
  without Bridge-injected state.
- Make `super3_packed_seq_compat_gpt_step` detectable by Megatron-Bridge
  `prepare_forward_step_func` state injection.
- Preserve direct two-argument local stub compatibility where practical.
- Keep `packed_seq_params` filtering scoped only to the model argument.

## Boundaries

- Product code/tests/task docs/status only.
- No live train, package install, endpoint, benchmark, W&B, cluster/deploy,
  artifact upload, direct `main`/`master` push, or self-merge.

## Status

- Base: `4fe9454e46343821f68e43c47cdeba1aaf0fef84`.
- Branch:
  `intern_nem_dev_1/task215_qwen_sft_packed_compat_bridge_state_injection_s1`.
- PR: https://github.com/songCNMS/Nemotron/pull/311
- Implementation head at PR open:
  `51fc113044039887410c8a4ff9da807940fc41ac`.
- PR state at open: open, mergeable, merge state `CLEAN`.
- Current implementation:
  - Renamed `packed_compat_step.forward_step` first parameter to `state` so
    Bridge state-injection detection can wrap it before Megatron-Core schedule
    calls.
  - Retained direct two-argument fallback for local stubs.
  - Updated focused tests to simulate
    `functools.partial(forward_step, state)(data_iterator, model)`.
- Checks completed so far:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_sft_packed_compat_step.py tests/recipes/super3/test_sft_forward_step_dispatch.py`
    -> `10 passed, 1 skipped`.
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_m1_agentic_sft.py -k 'qwen_local_train or qwen30b_a3b_local_train'`
    -> `10 passed, 86 deselected`.
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_qwen_chat_contract.py tests/recipes/super3/test_stage1_sft_default_config.py tests/recipes/super3/test_m1_agentic_sft.py -k 'qwen or sft or packed or data_prep or target_family'`
    -> `136 passed, 1 skipped`.
  - `/work-agents/.venv/bin/ruff check src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py tests/recipes/super3/test_sft_packed_compat_step.py tests/recipes/super3/test_sft_forward_step_dispatch.py`
    -> passed.
  - `/work-agents/.venv/bin/python -m py_compile src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py tests/recipes/super3/test_sft_packed_compat_step.py tests/recipes/super3/test_sft_forward_step_dispatch.py`
    -> passed.
  - Structured Bridge state-injection / no-live-surface probe ->
    `PM_TASK215_BRIDGE_STATE_INJECTION_STRUCTURED_PROBE_PASS`.
  - `git diff --check` -> passed.
  - `git diff --cached --check` -> passed before implementation commit.
- Blockers: none currently.
- Residual risk: no live SFT training rerun per PM boundary.
