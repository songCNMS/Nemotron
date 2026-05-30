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
- Released task219 one-iteration smoke passed with task218 `pip_target` first
  in `PYTHONPATH`: `task219_torchrun_rc=0`, iteration `1/1`, loss
  `1.195105E+01`, skipped/nan `0/0`.
- Checkpoint saved under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`
  on NemTron, size `1.2G`.
- Local CPU namespace did not see the checkpoint directory after the run, so
  checkpoint inventory/hash evidence is preserved in local-visible log
  `04_checkpoint_gpu_state_after_run.log`.
