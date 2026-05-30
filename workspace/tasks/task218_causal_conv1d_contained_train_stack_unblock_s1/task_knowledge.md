# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task218 must keep causal-conv1d source/wheel/build/install artifacts under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218`.
- Probe imports should compose `PYTHONPATH` from the task218 pip target,
  task209 mamba target, task209 Session 4 venv site-packages, and current
  `src`.
