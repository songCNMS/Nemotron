# History Log

<!-- METADATA:SESSION=7 -->

## Session 7 - 2026-05-30

- Accepted PM stop/finalization instruction after Session 6 observation. No
  further live launch, train workaround, full benchmark, package install,
  system mutation, process kill, endpoint, W&B, cluster, deploy, or artifact
  upload was attempted.
- Finalized the evidence-only task report with the exact Session 6 outcome:
  preflight passed with no SGLang/task210 process, no `:13000` listener, no
  H200 compute apps, and free torchrun master port `29531`; `:8000` remained
  documented-only and untouched.
- Session 6 canonical one-GPU Qwen-contract one-iteration smoke launched with
  `CUDA_VISIBLE_DEVICES=0`, reached model/dataloader setup and the training
  loop, then failed `rc=1` with `TypeError: MambaModel.forward() got an
  unexpected keyword argument 'packed_seq_params'`.
- Checkpoint state remains missing at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/checkpoints_one_iter`.
  Post-run evidence recorded H200s idle, no compute apps, `:13000` and `:29531`
  clear, and `:8000` still listening/documented-only.
- Final Session 6 evidence logs are under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs`:
  `01_session6_preflight_port_gpu.log`,
  `02_session6_canonical_one_iter_torchrun.log`,
  `03_session6_checkpoint_gpu_state_after_run.log`, and
  `04_local_visibility_copy_manifest.log`.

## Session 6 - 2026-05-30

- Accepted PM Session 6 direction to proceed under the tighter port rule:
  keep `:8000` untouched, require no SGLang/task210 process, no `:13000`
  listener, no H200 compute apps, and an explicit free torchrun master port.
- Ran/read-log preflight at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/01_session6_preflight_port_gpu.log`.
  Result: no SGLang/task210 process, no `:13000` listener, no compute apps,
  eight H200s idle, `:29531` free, and `:8000` still listening but documented
  only.
- Ran exactly one canonical single-GPU Qwen-contract smoke with:
  `CUDA_VISIBLE_DEVICES=0`, `--master_addr=127.0.0.1`,
  `--master_port=29531`, task208 staged sample splits, Session 5
  `mamba_ssm` `pip_target`, Session 4 venv site-packages, W&B disabled,
  manifest root null, `train.train_iters=1`, and `checkpoint.save_interval=1`.
  Log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/02_session6_canonical_one_iter_torchrun.log`.
- Result: `session6_torchrun_rc=1`. The run passed import blockers, initialized
  distributed, built the Qwen tokenizer, built the hybrid Mamba/MoE tiny model,
  built optimizer and packed-data iterators, then entered the training loop.
  It failed during the first forward pass with
  `TypeError: MambaModel.forward() got an unexpected keyword argument
  'packed_seq_params'`.
- Captured checkpoint/GPU/port state after the run in
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/03_session6_checkpoint_gpu_state_after_run.log`.
  No Session 6 checkpoint directory was created. H200s returned to idle, no
  compute apps were listed, `:13000` and `:29531` were clear, and `:8000`
  remained untouched/listening.
- Applied PM evidence-hygiene addendum by copying NemTron-only Session 5 logs
  `10_mamba_import_probe.log` through `13_checkpoint_state_no_launch.log` and
  Session 6 logs `01` through `03` into the local-visible shared artifact root.
  Copy manifest:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/04_local_visibility_copy_manifest.log`.
- Current blocker: canonical train stack now reaches the training loop, but the
  Megatron Bridge/Mamba model path rejects packed-sequence forward argument
  `packed_seq_params`.

## Session 5 - 2026-05-30

- Accepted PM Session 5 continuation to unblock `mamba_ssm` within task-owned
  paths only. Boundaries observed: no NemTron network, no system site mutation,
  no package install outside the task-owned venv/target, no multi-GPU/full
  train, and no W&B/cluster/deploy/artifact upload.
- Probed NemTron toolchain and GPU state. `/usr/local/cuda/bin/nvcc` exists,
  `gcc/g++` are 13.3.0, `cmake` is 3.31.1, `ninja` is present, Torch is
  `2.9.1+cu129`, `torch.version.cuda` is 12.9, CUDA is available with eight
  H200 devices, and no GPU compute apps were present.
- Searched existing local/VPN/NemTron stores for compatible `mamba-ssm` artifacts.
  No ready binary wheel was found. Fetched the `mamba_ssm-2.3.2.post1` sdist
  from the local package index into the task root, with SHA256
  `104cc47e9101e5401a675fa2b784f2952b9b037f3b1dd83b5ac544394e95d028`, and
  staged it to NemTron under `session5/source_artifacts`.
- Ran a contained forced source build on NemTron using the Session 4 venv and
  task-owned build target:

  ```bash
  TMPDIR="$BUILD_ROOT/tmp" PIP_CACHE_DIR="$BUILD_ROOT/cache" MAX_JOBS=1 \
  MAMBA_FORCE_BUILD=TRUE MAMBA_FORCE_CXX11_ABI=TRUE \
    "$VENV/bin/python" -m pip install --no-index --no-deps \
    --no-build-isolation --no-clean --target "$BUILD_ROOT/pip_target" "$SDIST"
  ```

  Result: `mamba_force_build_attempt_rc=0`. Built wheel:
  `mamba_ssm-2.3.2.post1-cp312-cp312-linux_x86_64.whl`, size `322163289`,
  SHA256 `45c1c2cb89f982f32f0739e871e9d4dadbbdb8c39b707673369a1ab8a34dfb55`.
- Persisted import evidence in
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/10_mamba_import_probe.log`.
  `mamba_ssm` and `selective_scan_cuda` import from
  `session5/build_mamba_force/pip_target`; Session 4 venv imports still pass for
  `nemo_run`, `megatron.energon`, `nvidia_resiliency_ext`, `torch`,
  `megatron`, and `megatron.bridge`.
- Ran final GPU/task210/SGLang preflight before any train launch. GPUs were idle
  and no compute apps were listed, but `ss` reported a listener on `0.0.0.0:8000`.
  Follow-up owner probe could not attribute the listener through `ss`, `lsof`,
  or `fuser`. Because the PM condition required no task210/SGLang/port/process
  before launching, no one-iteration smoke was started.
- Checkpoint state after the hold: Session 5
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/checkpoints_one_iter`
  is missing because no Session 5 train was launched. The older task root
  `checkpoints_one_iter` directory exists but no Session 5 checkpoint was
  created.
- Current status: train-stack import blockers are cleared in the user-owned venv
  plus Session 5 `pip_target`; remaining launch blocker is the unattributed
  `:8000` listener / task210 port preflight condition.

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
