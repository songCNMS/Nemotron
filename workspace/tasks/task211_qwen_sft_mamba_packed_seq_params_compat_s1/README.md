# task211_qwen_sft_mamba_packed_seq_params_compat_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=3 -->

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
- PR: https://github.com/songCNMS/Nemotron/pull/309
- Implementation head at PR open:
  `5d53b2396288c0a0cd4f570e0b22300d2468747e`.
- Final gated head:
  `0880c34fe80e15a2c43c01d92fc6a5a724ae48f2`.
- Merge commit on `main`:
  `f65dafdb15b28342c1fbd4a5ead807052bcdd264`.
- Closeout branch:
  `intern_nem_dev_1/task211_closeout_status_s3`.
- PR state at open: open, mergeable, merge state `CLEAN`.
- Session 2 closeout: status/report docs updated after PR open; current PR
  head is reported in `/work-agents/intern_nem_dev_1/report.md`.
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
  - Structured dispatch/config probe ->
    `PM_TASK211_PACKED_COMPAT_STRUCTURED_PROBE_PASS`.
  - `git diff --check` -> passed.
  - `git diff --cached --check` -> passed before implementation commit.
  - Session 2 final `git diff --check` / `git diff --cached --check` ->
    passed before docs/status closeout commit.
- Merge/closeout:
  - PR #309 was merged to `main` as
    `f65dafdb15b28342c1fbd4a5ead807052bcdd264` after replacement exact-head
    gate PASS.
  - Local `main` was fast-forwarded to the merge commit.
  - Dev status set to Idle / Current Task None.
- Blockers: none.
- Residual risk: no live training rerun performed per PM boundary; verification
  is static/unit coverage plus the prior task209 live failure log.
