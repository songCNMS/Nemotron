# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task219 is prepare-only until PM explicitly releases the live run after
  task218 exact-head verification.
- The task216 runtime blocker was
  `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`.
- Read-only task219 probe shows task218
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target`
  provides `causal_conv1d` and `causal_conv1d_cuda`.
- With task218 `pip_target` first in `PYTHONPATH`,
  `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_fwd_function` is not
  `None`.
- The future command must preserve PYTHONPATH order:
  task218 `pip_target`, task209 session5 Mamba target, task209 session4 venv
  site-packages, then task219 code checkout `src`.
- Re-probe GPU/process/port state before any PM-released train launch.
