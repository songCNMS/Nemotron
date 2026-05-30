# task209_nemtron_h200_sft_live_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Goal

Use the supervisor-provided NemTron H200 node to validate the Super3 Qwen SFT
live pipeline beyond local dry-runs.

## Baseline

`0460c1f0262875fb27ae530d30cd80d805752851`

## Resource Facts

- SSH alias: `NemTron`.
- PM observed hostname: `lg-cmc-b7r201-f08u26-h200-000126`.
- Expected GPUs: 8x NVIDIA H200.
- Qwen model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Artifact root: `/mnt/cephfs/data/nemotron-live-validation/task209`.

## Scope

- Run NemTron hostname, GPU, model, code, and Python import/CUDA preflight.
- Stage a source snapshot to cephfs if repo/code is not available on NemTron;
  do not `git pull` on NemTron.
- Wait for task208 sample splits:
  `/mnt/cephfs/data/nemotron-live-validation/task208/packed_qwen_sample4/splits`.
- Run one-iteration `m1_agentic_smoke` with Qwen model path and task208 sample
  splits if prerequisites are present.
- If smoke passes and full task208 splits exist, prepare the smallest safe
  SFT continuation command or report a PM scheduling hold.

## Boundaries

- No package, model, or container downloads on NemTron.
- No W&B, deploy, artifact upload, direct `main`/`master` push, or self-merge.
- Coordinate with dev_3 before any GPU endpoint serving.
