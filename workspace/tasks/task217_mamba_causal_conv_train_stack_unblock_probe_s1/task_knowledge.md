# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Task216 failing command used `/usr/local/bin/torchrun`; on NemTron that script
  has shebang `#!/usr/bin/python3`.
- Exact task216 train `PYTHONPATH`:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src`.
- `mamba_ssm==2.3.2.post1` is installed in the task209 Session 5 contained
  `pip_target`; `selective_scan_cuda` imports from the same target.
- `causal-conv1d` is not installed in the task209 train stack and no
  `causal_conv1d_cuda` extension is importable.
- In `mamba_ssm.ops.triton.ssd_combined`, the missing causal-conv1d import sets
  `causal_conv1d_fwd_function`, `causal_conv1d_bwd_function`, and
  `causal_conv1d_update_function` to `None`.
- Mamba metadata has optional extra `causal-conv1d>=1.2.0`; its README text
  recommends `causal-conv1d>=1.4.0`.
- Task209's internal package-index probe saw latest `causal-conv1d` version
  `1.6.2.post1`; prior task209 wheelhouse/source artifacts do not contain it.
- Unblock should build/install causal-conv1d into a task-owned target and prepend
  that target to `PYTHONPATH`; do not mutate `/usr/local` or the shared
  task209 venv.
- PM assigned the build/probe follow-up to dev_1 as task218; task217 remains
  no-launch/no-install diagnostic evidence only.
