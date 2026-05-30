# task218_causal_conv1d_contained_train_stack_unblock_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Evidence-only unblock probe for task216 runtime blocker
  `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`.
- Build or obtain a causal-conv1d package compatible with the NemTron train
  stack: Python 3.12, torch 2.9.1+cu129, triton 3.5.1, H200/sm90, task209
  Session 5 `mamba_ssm==2.3.2.post1` pip target, and task209 Session 4 venv
  site-packages.
- Keep build/install contained under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218`.
- Produce provenance, commands, logs, import/function probes, blockers if any,
  and one-iter rerun estimate.

## Boundaries

- Docs/status/evidence branch only; no product code edits.
- No training launch, endpoint/eval/benchmark, process kill, system/shared
  package mutation, model copy/download, W&B/cluster/deploy/artifact upload,
  direct `main`/`master` push, or self-merge.

## Status

- Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Branch:
  `intern_nem_dev_1/task218_causal_conv1d_contained_train_stack_unblock_s1`.
- Evidence root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218`.
- Current status: complete; evidence branch ready for PM handoff.
- Validation report:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/validation_report.md`
  with SHA-256
  `9bcd69ed88e12533d671321bc147fb20157320bd30d9f3c7bcdb7831eb53af09`.
- Source artifact:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/source_artifacts/causal_conv1d-1.6.2.post1.tar.gz`
  with SHA-256
  `245e314ea21064ded7a5bf6b3b842b644aa6f92e45cecfe3e935629744c35ff4`.
- Built wheel:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/wheelhouse/causal_conv1d-1.6.2.post1-cp312-cp312-linux_x86_64.whl`
  with SHA-256
  `347a4cf7d1b629162ce891cda40bdf5c20e1fa1da81ccc2e78467828e8f5ce6e`.
- Installed extension:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target/causal_conv1d_cuda.cpython-312-x86_64-linux-gnu.so`
  with SHA-256
  `b9b896d914d4dc90284863335bbc10a93099c2c49cdd969c0e57dcbded9e3497`.
- Required no-launch import/function probe:
  `TASK218_IMPORT_FUNCTION_PROBE_PASS`.
- Optional tiny direct CUDA extension smoke:
  `TASK218_TINY_CUDA_SMOKE_PASS`.
- Containment probe without task218 `pip_target`:
  `TASK218_CONTAINMENT_PROBE_PASS`.
- Blockers: none for causal-conv1d import/function unblock.
- Residual risk: no training rerun was launched by task218 boundary.
