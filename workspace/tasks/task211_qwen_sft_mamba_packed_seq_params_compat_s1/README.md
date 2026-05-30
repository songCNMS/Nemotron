# task211_qwen_sft_mamba_packed_seq_params_compat_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Fix the task209 Session 6 live Qwen-contract Stage1 SFT smoke failure:
  `TypeError: MambaModel.forward() got an unexpected keyword argument
  'packed_seq_params'`.
- Root-cause and patch the packed-sequence forward-step dispatch path without
  disabling packed-sequence behavior for models that support
  `packed_seq_params`.
- Add focused static/unit tests for the Mamba-incompatible path and the
  existing SFT forward-step dispatch surface.

## Boundaries

- Product code/config/tests/status docs only.
- No live train, package install, endpoint, benchmark, W&B, cluster deploy,
  artifact upload, direct `main`/`master` push, or self-merge.

## Status

- Base: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_1/task211_qwen_sft_mamba_packed_seq_params_compat_s1`.
- PR: pending.
- Current implementation:
  - Added `super3_packed_seq_compat_gpt_step` dispatch target.
  - Routed the tiny Stage1 SFT smoke config through the compatibility step.
  - The adapter delegates to upstream Megatron-Bridge `gpt_step` and filters
    `packed_seq_params` only when the unwrapped leaf model forward chain does
    not accept it.
- Checks completed so far:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_sft_packed_compat_step.py tests/recipes/super3/test_sft_forward_step_dispatch.py tests/recipes/super3/test_m1_agentic_sft.py -k 'qwen_local_train or qwen30b_a3b_local_train'`
    -> 10 passed, 95 deselected.
  - `/work-agents/.venv/bin/python -m py_compile src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py src/nemotron/recipes/super3/stage1_sft/step_dispatch.py tests/recipes/super3/test_sft_forward_step_dispatch.py tests/recipes/super3/test_sft_packed_compat_step.py`
    -> passed.
  - `/work-agents/.venv/bin/ruff check src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py src/nemotron/recipes/super3/stage1_sft/step_dispatch.py tests/recipes/super3/test_sft_forward_step_dispatch.py tests/recipes/super3/test_sft_packed_compat_step.py`
    -> passed after import formatting fix.
  - `git diff --check` -> passed.
- Blockers: none currently.
- Residual risk: no live training rerun performed per PM boundary; verification
  is static/unit coverage plus the prior task209 live failure log.
