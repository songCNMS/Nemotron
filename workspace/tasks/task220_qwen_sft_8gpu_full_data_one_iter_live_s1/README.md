# task220_qwen_sft_8gpu_full_data_one_iter_live_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Scope

- Validate a distributed 8-H200 Qwen3-30B-A3B Stage1 SFT smoke on product
  commit `1d037329f5a02cdc04f2a09a16e7342721be4c87` after the task219
  single-GPU smoke passed.
- Use full task208 packed data, task218/task209 train-stack overlays, and a
  task-owned code/config checkout under:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220`.
- Launch exactly one 8-GPU torchrun if preflight/data/resource checks pass.

## Status

- Result: PASS.
- Branch: `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1`.
- Product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220`.

## Evidence

- Full task208 data was not directly visible on NemTron at the original task208
  path, so it was staged by SSH tar with symlink dereference to:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full`.
- Staged split evidence and hashes:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/00_full_data_staging.log`.
- Code/config staging evidence:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/01_code_config_stage.log`.
- Resource preflight:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/02_preflight_resource.log`.
- Data stack/config probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/03_data_stack_config_probe.log`.
- Torchrun log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/04_canonical_8gpu_one_iter_torchrun.log`.
- Checkpoint and cleanup state:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/05_checkpoint_cleanup_state.log`.
- Local-visible artifact manifest:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/06_local_visibility_manifest.log`.

## Boundaries

- No second torchrun, workaround, package build/install, process kill,
  endpoint/eval/benchmark, full or multi-iteration training, W&B,
  cluster/deploy, artifact upload, main/master push, or self-merge.
