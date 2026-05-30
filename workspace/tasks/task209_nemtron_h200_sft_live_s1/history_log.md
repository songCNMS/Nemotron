# History Log

<!-- METADATA:SESSION=4 -->

## Session 4 - 2026-05-30

- Accepted PM train-stack unblock probe for task209 Session 4 with boundaries:
  no NemTron network download, no system Python/site-package mutation, and no
  multi-GPU/full train.
- Searched existing offline train-stack resources on NemTron, VPN, and local
  roots. NemTron had no conda/mamba/apptainer/singularity/docker environment or
  ready wheelhouse/container for the missing stack. VPN was reachable but did
  not expose the corrected cephfs task root. Local `/work-agents/.venv` had
  `nemo_run` but no Megatron stack.
- Built and staged a user-owned wheelhouse under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/wheelhouse`.
  The staged wheelhouse included the PM-requested missing packages
  `nemo-run`, `megatron-energon`, and `nvidia-resiliency-ext`, plus explicit
  resolver/runtime dependencies needed for import.
- Created a user-owned NemTron venv with system packages at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`.
  Offline resolver attempts exposed missing transitive dependencies
  (`grpcio>=1.76`, `invoke`, `h2`, then Torch metadata requiring an exact older
  `nvidia-cudnn-cu12`). To avoid CUDA runtime downgrades/system mutation, the
  final venv used `pip install --no-index --no-deps` for the staged wheels.
- Final no-launch import probe passed for `nemo_run`, `megatron.energon`,
  `nvidia_resiliency_ext`, `hydra`, `bracex`, `wcmatch.glob`, `torch`,
  `megatron`, and `megatron.bridge`; `mamba_ssm` remained absent.
- Reran single-GPU one-iteration smoke attempts while GPUs were still assigned
  to task209 and before PM's later SGLang hold:
  - venv site-packages attempt failed on missing `bracex`.
  - after `bracex`, it failed on missing `hydra`.
  - after `hydra`, the Qwen profile contract rejected `test_train.py` as a
    non-Qwen entrypoint.
  - a CLI override for `training_contract.train_entrypoint` was rejected by the
    Megatron recipe struct.
  - a session4-only Qwen contract config copy reached Megatron model build and
    failed on missing `mamba-ssm`.
- PM then issued a scheduling hold because task210 SGLang is running on NemTron
  with TP=8 and all H200s allocated. An attention-only tiny-pattern probe was
  already in flight; it completed with `rc=1`, reached the training loop, and
  failed with `MambaModel.forward() got an unexpected keyword argument
  'packed_seq_params'`.
- Confirmed after the PM hold that SGLang owned all eight H200s with scheduler
  processes on every GPU. No further train launch was started after the hold.
- Session 4 current state: target PM import blockers are unblocked in the
  user-owned venv, but canonical one-iteration smoke is blocked by missing
  `mamba-ssm`; noncanonical attention-only workaround is also blocked by the
  packed-sequence forward API mismatch. GPU execution is held pending PM
  release from task210.

## Session 3 - 2026-05-30

- Applied PM corrections for task209 sample staging after the local CPU and
  NemTron `/mnt/cephfs` namespaces diverged.
- Recorded the actual task208 sample source as
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4`.
- Reran sample staging with a single pipe-through-SSH command into
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4`.
  The command returned `staging_rc=0` and remote hashes matched local source
  hashes:
  - `blend.json`:
    `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
  - `splits/metadata.json`:
    `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
  - `splits/train/shard_000000.parquet`:
    `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`
- Ran the PM-authorized direct one-iteration `torchrun` fallback on
  `CUDA_VISIBLE_DEVICES=0` using the staged sample splits. It failed with
  `fallback_rc=1` before training because NemTron `/usr/bin/python3` imports
  `megatron.bridge` but then raises
  `ModuleNotFoundError: No module named 'megatron.energon'`.
- Confirmed the intended CLI path is also blocked because NemTron
  `/usr/bin/python3` lacks `nemo_run`.
- Probed bounded alternate Python environments on NemTron. Only
  `/usr/bin/python3` and `/usr/bin/python` were available; both expose
  `torch`, CUDA, `megatron`, and `megatron.bridge`, but neither has
  `nemo_run` or `megatron.energon`.
- Reran the local focused SFT/Qwen validator shard:
  `33 passed, 2 skipped`.
- Confirmed NemTron H200 GPUs were idle after the failed fallback: eight H200s,
  1 MiB used each, 0% utilization, no compute processes.
- Recorded PM's full split completion notice:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`
  with `total_sequences=987770`, `total_tokens=672687706`, `num_shards=16`,
  `pack_size=4096`, `elapsed_sec=254`. Full artifacts were not staged because
  the one-iteration smoke is blocked and PM review is required before any
  continuation.

## Session 2 - 2026-05-30

- PM corrected the artifact root and task208 handoff path while task209 setup
  was in progress.
- Updated task209 docs/status to use corrected artifact root
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209`.
- Updated the task208 sample split wait path to
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/splits`.
- Recorded that the earlier `/mnt/cephfs/data/nemotron-live-validation/...`
  root is superseded and must not receive new task209 outputs.
- Continued holding heavy NemTron GPU usage for dev_2/task209 until release or
  PM handoff.

## Session 1 - 2026-05-30

- Accepted PM assignment `task209_nemtron_h200_sft_live_s1`.
- Started from baseline `0460c1f0262875fb27ae530d30cd80d805752851`.
- Created evidence-only branch
  `intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`.
- Recorded task scope and boundaries before running NemTron commands.
- Coordinated with dev_3 that dev_2/task209 owns heavy NemTron GPU usage until
  release or PM handoff; dev_3 may do only non-heavy discovery.
