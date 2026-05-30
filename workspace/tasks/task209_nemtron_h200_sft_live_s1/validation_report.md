# task209 Validation Report

<!-- METADATA:SESSION=6 -->

## Baseline

- Product baseline: `0460c1f0262875fb27ae530d30cd80d805752851`
- Branch: `intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`
- Corrected artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209`
- Qwen model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

## Logs

- NemTron preflight:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/01_nemtron_preflight_corrected.log`
- Staged source snapshot:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/02_stage_source_snapshot_corrected.log`
- Intended CLI feasibility failure:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/03_post_stage_cli_feasibility_corrected.log`
- Corrected task208 sample path and namespace probes:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/05_task208_corrected_sample4_probe.log`
  through
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/08_local_processing_mount_probe.log`
- PM-corrected single-SSH sample staging:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/13_stage_task208_sample4_pm_single_ssh.log`
- Direct torchrun fallback after verified staging:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/14_direct_torchrun_one_iter_after_pm_staging.log`
- Bounded alternate Python probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/15_nemtron_alternate_python_probe.log`
- Local focused validators:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/16_local_sft_qwen_validators.log`
- Post-fallback GPU idle probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/logs/17_nemtron_gpu_idle_after_fallback.log`

## Commands And Results

### Sample Staging

```bash
SRC=/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4
DEST=/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4
(cd "$SRC" && tar --dereference -cf - blend.json splits) | ssh -o BatchMode=yes NemTron "rm -rf '$DEST' && mkdir -p '$DEST' && tar -C '$DEST' -xf - && find '$DEST' -maxdepth 4 -type f -printf '%p %s\n' && sha256sum '$DEST'/blend.json '$DEST'/splits/metadata.json '$DEST'/splits/train/shard_000000.parquet"
```

Result: `staging_rc=0`.

Matched hashes:

- `blend.json`:
  `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
- `splits/metadata.json`:
  `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
- `splits/train/shard_000000.parquet`:
  `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`

### Direct Torchrun Fallback

```bash
ssh -o BatchMode=yes NemTron "cd '/mnt/cephfs/data/processing/nemotron-live-validation/task209/Nemotron' && \
PYTHONPATH=src \
NEMO_RUN_DIR='/mnt/cephfs/data/processing/nemotron-live-validation/task209' \
SUPER3_M1_AGENTIC_PACKED_DIR='/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits' \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE='/mnt/cephfs/data/processing/nemotron-live-validation/task209/checkpoints_one_iter' \
CUDA_VISIBLE_DEVICES=0 \
torchrun --nproc_per_node=1 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_smoke.yaml \
  train.train_iters=1 \
  checkpoint.save_interval=1 \
  artifacts.wandb=false \
  artifacts.manifest.root=null"
```

Result: `fallback_rc=1`.

Failure:

```text
ModuleNotFoundError: No module named 'megatron.energon'
```

The failure occurs while importing Megatron Bridge recipe modules, before train
start or checkpoint creation.

### Alternate Python Probe

Result: probe succeeded, but no complete train environment was found.

- `/usr/bin/python3`: `torch=True`, CUDA available, 8 devices,
  `megatron=True`, `megatron.bridge=True`, `nemo_run=False`,
  `megatron.energon=False`.
- `/usr/bin/python`: same result.
- `/opt/conda` and `/opt/venv`: absent.

### Local Focused Validators

```bash
PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q \
  tests/recipes/super3/test_stage1_sft_train_bridge.py \
  tests/recipes/super3/test_sft_forward_step_dispatch.py \
  tests/recipes/super3/test_qwen_chat_contract.py \
  tests/recipes/super3/test_eval_chat_template_kwargs.py
```

Result: `33 passed, 2 skipped`, `validator_rc=0`.

## Blockers

- Intended CLI launcher is blocked because NemTron `/usr/bin/python3` lacks
  `nemo_run`.
- Direct one-iteration fallback is blocked because the available NemTron Python
  environments lack `megatron.energon`.
- No package install or download was attempted on NemTron.

## Continuation Status

PM reported full task208 splits are available locally at:

`/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`

Metrics: `total_sequences=987770`, `total_tokens=672687706`,
`num_shards=16`, `pack_size=4096`, `elapsed_sec=254`.

Full artifacts were not staged and no full/small continuation was launched
because the one-iteration smoke did not pass and PM review is required before
any continuation.

Post-fallback GPU probe showed eight H200s at 1 MiB used, 0% utilization, and
no compute processes.

## Session 4 Train-Stack Unblock Probe

Session 4 root:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4`

### Existing Resource Search

Logs:

- NemTron resource search:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/01_nemtron_offline_resource_search.log`
- Local resource search:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/02b_local_narrow_resource_search.log`
- VPN resource search:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/03_vpn_offline_resource_search.log`

Result: no ready offline conda/venv/container/wheelhouse was found. Local
`/work-agents/.venv` had `nemo_run` but no Megatron stack.

### Wheelhouse And Venv

- Local wheelhouse build:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/local_wheelhouse_build`
- Staged NemTron wheelhouse:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/wheelhouse`
- User-owned NemTron venv:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`

Key logs:

- Initial target wheel download:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/04_local_wheelhouse_download_nodeps.log`
- Dependency presence probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/06_nemtron_dependency_presence_probe.log`
- Wheelhouse staging:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/08_stage_wheelhouse_to_nemtron.log`
- Resolver install attempts:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/09_nemtron_create_venv_install_attempt1.log`
  through
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/21_nemtron_venv_install_attempt4.log`
- Final no-deps venv install:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/23_nemtron_venv_install_attempt5_nodeps_all_wheels.log`
- Additional runtime dependency installs:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/26_stage_install_bracex.log`
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/28_local_stage_install_hydra_core.log`

Final import probe:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/35_session4_final_import_probe_no_launch.log`

Result:

- Import passes: `nemo_run`, `megatron.energon`, `nvidia_resiliency_ext`,
  `hydra`, `bracex`, `wcmatch.glob`, `torch`, `megatron`, `megatron.bridge`.
- Import fails: `mamba_ssm`.

No package was installed into `/usr/bin/python3` or system site-packages. NemTron
network was not used.

### One-Iteration Smoke Attempts

These were run before the PM task210 SGLang GPU hold arrived, except the
attention-only probe was already in flight when the hold message arrived.

- Venv site-packages run:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/24_session4_direct_torchrun_one_iter.log`
  failed on missing `bracex`.
- After `bracex`:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/27_session4_direct_torchrun_one_iter_after_bracex.log`
  failed on missing `hydra`.
- After `hydra`:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/29_session4_direct_torchrun_one_iter_after_hydra.log`
  failed the Qwen training contract because `test_train.py` is not a Qwen
  entrypoint.
- CLI entrypoint override attempt:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/30_session4_direct_torchrun_one_iter_with_qwen_entrypoint_override.log`
  failed because Hydra could not override `training_contract.train_entrypoint`
  on the Megatron recipe struct.
- Session4 Qwen contract config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/m1_agentic_smoke_qwen_contract.yaml`
- Canonical Qwen-contract run:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/32_session4_direct_torchrun_one_iter_qwen_contract_config.log`
  reached Megatron model build and failed with `MambaSSM is not installed`.
- `mamba-ssm` binary probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/33_local_wheelhouse_download_mamba_ssm_binary_probe.log`
  found no matching binary wheel in the local index.
- Noncanonical attention-only tiny-pattern probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/34_session4_direct_torchrun_one_iter_attention_only_probe.log`
  reached the training loop and failed with
  `MambaModel.forward() got an unexpected keyword argument 'packed_seq_params'`.

### GPU Hold

PM issued a scheduling hold because task210 SGLang TP=8 is active on NemTron.
No further train smoke may be launched until PM explicitly releases GPUs.

GPU state log:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/logs/36_nemtron_gpu_state_after_pm_hold.log`

Result: all eight H200s had `sglang::scheduler_TP*` compute processes with
about 132 GB allocated per GPU.

### Prepared Command After PM Release

Do not run this until PM releases NemTron GPUs. It is the canonical
Qwen-contract one-iteration command, but it is expected to remain blocked by
missing `mamba-ssm` unless PM provides or authorizes a compatible package/env:

```bash
ssh -o BatchMode=yes NemTron "cd '/mnt/cephfs/data/processing/nemotron-live-validation/task209/Nemotron' && \
PYTHONPATH='/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:src' \
NEMO_RUN_DIR='/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4' \
SUPER3_M1_AGENTIC_PACKED_DIR='/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits' \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE='/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/checkpoints_one_iter' \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config '/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/m1_agentic_smoke_qwen_contract.yaml' \
  train.train_iters=1 \
  checkpoint.save_interval=1 \
  artifacts.wandb=false \
  artifacts.manifest.root=null"
```

## Session 5 Mamba Source-Build Unblock Probe

Session 5 root:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5`

### Logs

- Toolchain/GPU probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/01_nemtron_toolchain_gpu_probe.log`
- Artifact searches:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/02_local_mamba_artifact_search.log`
  through
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/04_nemtron_mamba_artifact_search.log`
- Local sdist fetch and inspection:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/06_local_direct_fetch_mamba_sdist.log`
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/07_local_inspect_mamba_sdist_setup.log`
- Staged sdist to NemTron:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/08_stage_mamba_sdist_to_nemtron.log`
- Contained source build:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/09_nemtron_mamba_force_build_attempt.log`
- Import probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/10_mamba_import_probe.log`
- Final GPU/task210/SGLang preflight:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/11_final_gpu_sglang_preflight.log`
- Port owner probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/12_port8000_owner_probe.log`
- Checkpoint state:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/logs/13_checkpoint_state_no_launch.log`

### Toolchain And Artifact Result

NemTron toolchain probe passed for a contained source-build attempt:
`/usr/local/cuda/bin/nvcc` exists, `gcc/g++` are 13.3.0, `cmake` is 3.31.1,
`ninja` is available, Torch is `2.9.1+cu129`, Torch CUDA is 12.9, and CUDA sees
eight H200 devices.

No ready local/VPN/NemTron binary wheel was found. The staged sdist was:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/source_artifacts/mamba_ssm-2.3.2.post1.tar.gz`

SHA256:

`104cc47e9101e5401a675fa2b784f2952b9b037f3b1dd83b5ac544394e95d028`

### Build Command And Result

```bash
TMPDIR="$BUILD_ROOT/tmp" PIP_CACHE_DIR="$BUILD_ROOT/cache" MAX_JOBS=1 \
MAMBA_FORCE_BUILD=TRUE MAMBA_FORCE_CXX11_ABI=TRUE \
  "$VENV/bin/python" -m pip install --no-index --no-deps \
  --no-build-isolation --no-clean --target "$BUILD_ROOT/pip_target" "$SDIST"
```

Where:

- `VENV=/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`
- `SDIST=/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/source_artifacts/mamba_ssm-2.3.2.post1.tar.gz`
- `BUILD_ROOT=/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force`

Result: `mamba_force_build_attempt_rc=0`.

Built wheel:

- File: `mamba_ssm-2.3.2.post1-cp312-cp312-linux_x86_64.whl`
- Size: `322163289`
- SHA256:
  `45c1c2cb89f982f32f0739e871e9d4dadbbdb8c39b707673369a1ab8a34dfb55`

Install target:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`

No install was made into NemTron system Python or system site-packages.

### Import Probe

Command shape:

```bash
PYTHONPATH="$TARGET:$VENV/lib/python3.12/site-packages" \
  "$VENV/bin/python" - <<'PY'
import mamba_ssm
from mamba_ssm.ops.selective_scan_interface import selective_scan_fn
import selective_scan_cuda
PY
```

Result: `import_probe_rc=0`.

Confirmed imports:

- `mamba_ssm` from
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target/mamba_ssm/__init__.py`
- `selective_scan_cuda` from
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target/selective_scan_cuda.cpython-312-x86_64-linux-gnu.so`
- Session 4 venv remains usable for `nemo_run`, `megatron.energon`,
  `nvidia_resiliency_ext`, `torch`, `megatron`, and `megatron.bridge`.

`causal_conv1d` was not present, but the direct `mamba_ssm` and
`selective_scan_cuda` import probe passed.

### Final Launch Preflight And Hold

Final GPU preflight at `2026-05-30T17:34:03Z` showed all eight H200s idle with
about 1 MiB used per GPU and no compute apps. The same preflight found a
listener on `0.0.0.0:8000`.

Follow-up owner probe:

```bash
ss -ltnp "( sport = :8000 )"
lsof -nP -iTCP:8000 -sTCP:LISTEN
fuser -v 8000/tcp
```

Result: `ss` still showed `0.0.0.0:8000` listening, while `lsof` and `fuser`
did not attribute an owner. Because PM's Session 5 condition required no
task210/SGLang/port/process before launch, the canonical one-iteration smoke was
not started.

Prepared but not launched:

```bash
ssh -o BatchMode=yes NemTron "cd '/mnt/cephfs/data/processing/nemotron-live-validation/task209/Nemotron' && \
PYTHONPATH='/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:src' \
NEMO_RUN_DIR='/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5' \
SUPER3_M1_AGENTIC_PACKED_DIR='/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits' \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE='/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/checkpoints_one_iter' \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config '/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/m1_agentic_smoke_qwen_contract.yaml' \
  train.train_iters=1 \
  checkpoint.save_interval=1 \
  artifacts.wandb=false \
  artifacts.manifest.root=null"
```

### Checkpoint State

- Session 5 checkpoint path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/checkpoints_one_iter`
  is missing because no Session 5 train was launched.
- Older task root checkpoint directory exists:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/checkpoints_one_iter`
- Session 4 checkpoint path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/checkpoints_one_iter`
  is missing.

### Estimates And Resource Request

- One-iteration smoke: ready to run after PM clears or attributes the `:8000`
  listener; expected command is above and uses one H200 through
  `CUDA_VISIBLE_DEVICES=0`.
- Small pilot: still gated on one-iteration evidence. A safe next pilot should
  use the staged sample or a single full shard after PM review, W&B disabled,
  and an explicit checkpoint path under the task root.
- Full train: task208 full split metadata reports `987770` packed sequences and
  `672687706` tokens across 16 shards. With the smoke config's
  `global_batch_size=1`, one full pass would be `987770` optimizer iterations;
  reliable wall-clock cannot be estimated until the one-iteration smoke produces
  real step-time evidence on the intended config.

Current blocker: `READY_HELD_PORT_BUSY`; imports are unblocked, GPUs are idle,
but `0.0.0.0:8000` is still listening and unattributed.

## Session 6 Canonical One-Iteration Smoke

Session 6 root:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6`

### Logs

- Preflight:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/01_session6_preflight_port_gpu.log`
- Canonical torchrun:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/02_session6_canonical_one_iter_torchrun.log`
- Checkpoint/GPU state after run:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/03_session6_checkpoint_gpu_state_after_run.log`
- Local-visible log copy manifest:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/04_local_visibility_copy_manifest.log`

### Preflight

PM tightened the Session 6 port rule: keep `:8000` untouched, but require no
SGLang/task210 process, no `:13000` listener, no H200 compute apps, and an
explicit free high torchrun master port.

Preflight result:

- no SGLang/task210 process found
- no `:13000` listener
- no H200 compute apps
- eight H200s idle, about 1 MiB used and 0% utilization
- `:29531` free and selected as the torchrun master port
- `:8000` still listening on `0.0.0.0:8000`; documented and left untouched

### Command

Exactly one canonical single-GPU Qwen-contract smoke was launched:

```bash
ssh -o BatchMode=yes NemTron 'cd "/mnt/cephfs/data/processing/nemotron-live-validation/task209/Nemotron" && \
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29531 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 \
  checkpoint.save_interval=1 \
  artifacts.wandb=false \
  artifacts.manifest.root=null'
```

### Result

Result: `session6_torchrun_rc=1`.

The run successfully passed the previous missing-package blockers:

- `mamba_ssm` / `selective_scan_cuda` loaded from the Session 5 `pip_target`
- `nemo_run`, `megatron.energon`, `nvidia_resiliency_ext`, Torch/CUDA,
  Megatron, and Megatron Bridge were available through the Session 4 venv and
  system site packages
- distributed initialization completed
- Qwen tokenizer was built from
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- hybrid Mamba/MoE tiny model, optimizer, scheduler, and packed-data iterators
  were built
- training loop started at iteration 0

Failure:

```text
TypeError: MambaModel.forward() got an unexpected keyword argument 'packed_seq_params'
```

This occurred during the first training forward pass through
`megatron.bridge.training.gpt_step._forward_step_common` into the wrapped
`MambaModel`. The smoke stopped after this single run as requested.

### Checkpoint State

Checkpoint target:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/checkpoints_one_iter`

State: missing. No checkpoint was created because the first forward pass failed
before the configured `checkpoint.save_interval=1` save point.

Post-run state:

- no H200 compute apps
- all eight H200s idle
- no `:13000` listener
- no `:29531` listener
- `:8000` still listening and untouched

### Evidence Visibility

PM noted that the local/test view of the shared artifact root could see only
Session 5 logs `01` through `09`. I copied the referenced NemTron-only logs into
the local-visible shared artifact root without rerunning probes:

- `session5/logs/10_mamba_import_probe.log`
- `session5/logs/11_final_gpu_sglang_preflight.log`
- `session5/logs/12_port8000_owner_probe.log`
- `session5/logs/13_checkpoint_state_no_launch.log`
- `session6/logs/01_session6_preflight_port_gpu.log`
- `session6/logs/02_session6_canonical_one_iter_torchrun.log`
- `session6/logs/03_session6_checkpoint_gpu_state_after_run.log`

Manifest:

`/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/04_local_visibility_copy_manifest.log`

Remote and local SHA256s matched for the copied NemTron logs. The copy command
returned `copy_rc=0`.

### Current Blocker And Estimate

Current blocker: `MAMBA_PACKED_SEQ_PARAMS_API_MISMATCH`. The canonical train
stack now reaches the first training forward pass, but the Mamba model forward
path does not accept the packed-sequence argument emitted by the Megatron Bridge
packed SFT forward step.

Small/full continuation remains blocked until this API mismatch is fixed or PM
approves a non-packed/attention-only alternative. Full train estimate is still
gated on a successful one-iteration step-time measurement. The full task208
metadata remains `987770` packed sequences and `672687706` tokens across 16
shards; with `global_batch_size=1`, one full pass would require `987770`
optimizer iterations.
