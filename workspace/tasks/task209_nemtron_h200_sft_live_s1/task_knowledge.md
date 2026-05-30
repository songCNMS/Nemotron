# Task Knowledge

<!-- METADATA:SESSION=5 -->

- Baseline commit: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`.
- NemTron SSH alias: `NemTron`.
- Corrected artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209`.
- Qwen model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Actual task208 sample split source:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`.
- NemTron-visible staged sample split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Correct sample staging must use a pipe-through-SSH command that creates and
  extracts in the NemTron namespace:
  `(cd "$SRC" && tar --dereference -cf - blend.json splits) | ssh -o BatchMode=yes NemTron "rm -rf '$DEST' && mkdir -p '$DEST' && tar -C '$DEST' -xf - && find '$DEST' -maxdepth 4 -type f -printf '%p %s\n' && sha256sum '$DEST'/blend.json '$DEST'/splits/metadata.json '$DEST'/splits/train/shard_000000.parquet"`.
- One-iteration checkpoint path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/checkpoints_one_iter`.
- Intended CLI blocker: NemTron `/usr/bin/python3` lacks `nemo_run`.
- Direct `torchrun` fallback blocker: NemTron `/usr/bin/python3` has
  `torch`, CUDA, `megatron`, and `megatron.bridge`, but lacks
  `megatron.energon`, causing `ModuleNotFoundError` before train start.
- Bounded alternate Python probe found no usable complete environment:
  `/usr/bin/python3` and `/usr/bin/python` both lack `nemo_run` and
  `megatron.energon`; `/opt/conda` and `/opt/venv` are absent.
- PM-reported task208 full split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`
  (`total_sequences=987770`, `total_tokens=672687706`, `num_shards=16`,
  `pack_size=4096`, `elapsed_sec=254`). Do not launch full/small continuation
  until PM reviews the one-iteration evidence.
- Session 4 user-owned wheelhouse path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/wheelhouse`.
- Session 4 user-owned NemTron venv path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`.
- Session 4 venv import status: `nemo_run`, `megatron.energon`,
  `nvidia_resiliency_ext`, `hydra`, `bracex`, `wcmatch.glob`, `torch`,
  `megatron`, and `megatron.bridge` import; `mamba_ssm` does not.
- Resolver note: normal offline `pip install --no-index` reached Torch metadata
  requiring `nvidia-cudnn-cu12==9.10.2.21`, while the system has
  `nvidia-cudnn-cu12==9.16.0.29` and Torch/CUDA imports. Do not downgrade CUDA
  runtime packages without PM approval.
- Canonical Qwen-contract smoke config copy:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/m1_agentic_smoke_qwen_contract.yaml`.
- Canonical one-iteration command remains blocked by missing `mamba-ssm` in the
  NemTron environment; binary wheel probe for `mamba-ssm` returned no matching
  distribution from the local package index.
- Noncanonical attention-only tiny-pattern probe avoided `mamba-ssm` but failed
  at train-loop forward with `MambaModel.forward() got an unexpected keyword
  argument 'packed_seq_params'`.
- PM task210 hold: SGLang TP=8 is active on all NemTron H200s. Do not launch
  any train smoke until PM explicitly releases GPUs.
- Session 5 mamba source-build root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force`.
- Session 5 staged mamba sdist:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/source_artifacts/mamba_ssm-2.3.2.post1.tar.gz`
  with SHA256
  `104cc47e9101e5401a675fa2b784f2952b9b037f3b1dd83b5ac544394e95d028`.
- Session 5 contained build result: `mamba_ssm-2.3.2.post1` built successfully
  with `MAMBA_FORCE_BUILD=TRUE`, `MAMBA_FORCE_CXX11_ABI=TRUE`, `MAX_JOBS=1`,
  `--no-index`, `--no-deps`, `--no-build-isolation`, and `--target
  session5/build_mamba_force/pip_target`; no system Python/site-packages were
  modified.
- Session 5 import status: with `PYTHONPATH` prepending
  `session5/build_mamba_force/pip_target` and the Session 4 venv site-packages,
  `mamba_ssm`, `selective_scan_cuda`, `nemo_run`, `megatron.energon`,
  `nvidia_resiliency_ext`, `torch`, `megatron`, and `megatron.bridge` import.
  `causal_conv1d` remains absent, but the direct `mamba_ssm` and
  `selective_scan_cuda` import probe passed.
- Session 5 final GPU preflight found all eight H200s idle and no compute apps,
  but `0.0.0.0:8000` was listening and could not be attributed by `ss`, `lsof`,
  or `fuser`; no one-iteration train was launched under the PM
  no-task210/SGLang/port/process condition.
- Prepared Session 5 canonical single-GPU command if PM clears the port hold:
  use `PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:src`,
  `NEMO_RUN_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5`,
  `SUPER3_M1_AGENTIC_PACKED_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`,
  and checkpoint save
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/checkpoints_one_iter`.
- NemTron has no network: do not download packages, models, containers, or run
  `git pull` on NemTron.
- dev_2/task209 owns heavy NemTron GPU usage until release or PM handoff.
- Superseded root: do not write new task209 outputs under
  `/mnt/cephfs/data/nemotron-live-validation/...`.
