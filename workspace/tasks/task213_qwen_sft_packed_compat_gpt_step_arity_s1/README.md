# task213_qwen_sft_packed_compat_gpt_step_arity_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Fix the task212 evidence failure in
  `src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py`.
- Preserve Megatron-Bridge state-aware `gpt_step` arity:
  `(state, data_iterator, model, return_schedule_plan=False)`.
- Keep compatibility with existing local two-argument test stubs where
  reasonable.
- Continue filtering `packed_seq_params` only around the model argument, and
  only for model forward chains that do not support that keyword.

## Boundaries

- Product code/tests/docs only.
- No live train, package install, endpoint, benchmark, W&B, cluster/deploy,
  artifact upload, direct `main`/`master` push, or self-merge.

## Status

- Base: `f65dafdb15b28342c1fbd4a5ead807052bcdd264`.
- Branch: `intern_nem_dev_1/task213_qwen_sft_packed_compat_gpt_step_arity_s1`.
- PR: https://github.com/songCNMS/Nemotron/pull/310
- Implementation head at PR open:
  `469984005a6c6f9148715c507429a66973ed0231`.
- PR state at open: open, mergeable, merge state `CLEAN`.
- Session 2 ready-for-gate docs/status follow-up: committed after PR open;
  replacement exact head is reported in `/work-agents/intern_nem_dev_1/report.md`.
- Current implementation:
  - `packed_compat_step.forward_step` now accepts the runtime
    state-aware Bridge call shape and passes `state`, `data_iterator`, `model`,
    and `return_schedule_plan` through to upstream `gpt_step`.
  - Existing two-argument stub behavior is retained for local static tests.
  - Focused tests now cover state-aware Mamba-like drop, packed-aware preserve,
    `return_schedule_plan` propagation, legacy two-arg behavior, and dispatch
    wiring.
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
  - Structured arity/config probe ->
    `PM_TASK213_PACKED_COMPAT_ARITY_STRUCTURED_PROBE_PASS`.
  - `git diff --check` -> passed.
  - `git diff --cached --check` -> passed before implementation commit.
- Blockers: none currently.
- Residual risk: no live SFT training rerun per PM boundary.
