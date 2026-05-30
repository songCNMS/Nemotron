# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-30

- Accepted PM task218 on branch
  `intern_nem_dev_1/task218_causal_conv1d_contained_train_stack_unblock_s1`
  from exact base `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Scope is evidence-only docs/status/probe work to unblock missing
  causal-conv1d callables for the Mamba SSM train stack without launching
  training or mutating shared Python environments.
- Confirmed prior task216/task217 root cause: `mamba_ssm==2.3.2.post1` and
  `selective_scan_cuda` were present, but `causal_conv1d`,
  `causal_conv1d_cuda`, and Mamba `ssd_combined` causal-conv1d callables were
  missing or `None`.
- Fetched `causal-conv1d==1.6.2.post1` sdist locally, recorded SHA-256
  provenance, and staged it by tar over SSH because the local CPU-created file
  was not visible from NemTron through the same Ceph path.
- Built the wheel on NemTron with task209 Session 4 venv Python, torch
  `2.9.1+cu129`, CUDA `12.9`, triton `3.5.1`, no build isolation, no deps,
  and task-owned cache/wheel directories.
- Installed the wheel only into the task-owned
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target`.
- Required no-launch import/function probe passed with task218 `pip_target`
  prepended before task209 Mamba target and task209 Session 4 venv site.
- Optional tiny direct CUDA extension smoke passed for `causal_conv1d_fn` and
  `causal_conv1d_update`; no torchrun, dataloader, model training, or
  benchmark was launched.
- Containment probe passed: without task218 `pip_target`, the old stack still
  lacks `causal_conv1d` and Mamba callables remain `None`, confirming no
  shared/global package mutation.
- Wrote and staged validation report at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/validation_report.md`.
