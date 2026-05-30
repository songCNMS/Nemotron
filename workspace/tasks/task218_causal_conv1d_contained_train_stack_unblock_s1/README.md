# task218_causal_conv1d_contained_train_stack_unblock_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

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
- Current status: accepted; context inspection and contained artifact probe in
  progress.
