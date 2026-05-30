# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-30

- Accepted PM task211 on branch
  `intern_nem_dev_1/task211_qwen_sft_mamba_packed_seq_params_compat_s1`
  at base `0460c1f0262875fb27ae530d30cd80d805752851`.
- Read task209 Session 6 live evidence log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/02_session6_canonical_one_iter_torchrun.log`.
- Root cause: the tiny Stage1 SFT smoke config uses packed sequence specs,
  upstream Megatron-Bridge `gpt_step` forwards `packed_seq_params`, and the
  active Mamba leaf model forward does not accept that keyword.
- Added `packed_compat_step.py`, a local `gpt_step` adapter that preserves
  upstream packed-sequence behavior when the unwrapped model forward supports
  `packed_seq_params`, and filters only the unsupported Mamba-style keyword.
- Registered `super3_packed_seq_compat_gpt_step` in the SFT forward-step
  dispatch table and routed `config/test.yaml` to it.
- Added focused tests for the Mamba-like no-`packed_seq_params` path, the
  packed-aware preservation path, dispatch registration, and tiny smoke config
  wiring.
