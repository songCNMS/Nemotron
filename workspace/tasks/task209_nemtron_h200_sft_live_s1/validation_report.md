# task209 Validation Report

<!-- METADATA:SESSION=3 -->

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
