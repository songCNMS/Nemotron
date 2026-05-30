# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task218 must keep causal-conv1d source/wheel/build/install artifacts under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218`.
- Probe imports should compose `PYTHONPATH` from the task218 pip target,
  task209 mamba target, task209 Session 4 venv site-packages, and current
  `src`.
- The local CPU host has a mismatched Python stack for this build
  (`torch==2.7.0a0+...`, CUDA 12.8, no visible GPU), so the compatible wheel
  must be built on NemTron against task209 Session 4 venv torch
  `2.9.1+cu129` and CUDA 12.9.
- CPU-created files under the task218 Ceph path were not visible from NemTron;
  use explicit tar/SSH staging for source/report artifacts that NemTron must
  consume.
- `CAUSAL_CONV1D_FORCE_BUILD=TRUE` avoids the package's prebuilt-wheel URL path
  and forces a local contained build suitable for NemTron with no network.
- Prepending task218 `pip_target` makes
  `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_fwd_function`,
  `causal_conv1d_bwd_function`, and `causal_conv1d_update_function` callable.
