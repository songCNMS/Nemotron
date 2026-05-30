# Task206 Train Stack Unblock Probe

<!-- METADATA:SESSION=1 -->

## Summary

- Owner: `intern_nem_dev_2`.
- Branch: `intern_nem_dev_2/task206_qwen_sft_train_stack_unblock_probe_s1`.
- Baseline: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Evidence root: `/tmp/nemotron-live-validation/task206`.
- Result: dry-run and validators passed; no available local/project environment
  satisfies the one-iteration smoke prerequisites.

## Environment And Resource Status

- Primary Python: `/work-agents/.venv/bin/python`.
- Primary Python results:
  - `torch`: missing.
  - `megatron`: missing.
  - `megatron.bridge`: missing.
  - `nemo_run`: present.
  - CUDA status: unavailable because `torch` is missing.
- `conda env list`: `conda` not found.
- Bounded alternate venv inventory:
  - Only `/work-agents/.venv/bin/python` was discovered under the allowed
    `/work-agents/*/.venv/bin/python` and obvious project-venv paths.
  - No alternate Python with `torch`, `megatron`, and `megatron.bridge` was
    found.
- GPU visibility: `nvidia-smi` not found.
- Qwen model path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507` is missing.
- Fresh task205 packed splits:
  `/tmp/nemotron-live-validation/task205/packed_qwen/splits` is missing.
- Fallback task071 packed splits:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`
  exists.
- Fallback task071 blend:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/blend.json`
  exists.

## Commands And Results

1. Primary venv train-stack probe:

```bash
PYTHONPATH=src /work-agents/.venv/bin/python - <<'PY'
import importlib
mods = ["torch", "megatron", "megatron.bridge", "nemo_run"]
for mod in mods:
    importlib.import_module(mod)
PY
```

Result: probe completed with caught import results; `nemo_run=True`,
`torch=False`, `megatron=False`, `megatron.bridge=False`.
Log: `/tmp/nemotron-live-validation/task206/logs/01_primary_venv_probe.log`.

2. Bounded alternate env inventory:

```bash
conda env list || true
for py in /work-agents/.venv/bin/python /work-agents/*/.venv/bin/python \
  /work-agents/intern_nem_dev_2/.venv/bin/python \
  /work-agents/intern_nem_dev_2/Nemotron/.venv/bin/python; do
  [ -x "$py" ] && timeout 30 "$py" - <<'PY'
import importlib
for mod in ["torch", "megatron", "megatron.bridge", "nemo_run"]:
    importlib.import_module(mod)
PY
done
```

Result: `conda` not found; only `/work-agents/.venv/bin/python` discovered;
same missing stack as primary probe.
Log: `/tmp/nemotron-live-validation/task206/logs/02_bounded_env_inventory.log`.

3. GPU/model/packed-data probe:

```bash
nvidia-smi -L
test -e /mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507
test -e /tmp/nemotron-live-validation/task205/packed_qwen/splits
test -e /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits
test -e /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/blend.json
```

Result: `nvidia-smi` not found; Qwen path missing; task205 splits missing;
fallback task071 splits and blend exist.
Log: `/tmp/nemotron-live-validation/task206/logs/03_gpu_model_data_probe.log`.

4. Mandatory SFT dry-run:

```bash
PYTHONPATH=src \
NEMO_RUN_DIR=/tmp/nemotron-live-validation/task206 \
SUPER3_M1_AGENTIC_PACKED_DIR=/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits \
SUPER3_M1_TOKENIZER_MODEL=/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE=/tmp/nemotron-live-validation/task206/checkpoints \
/work-agents/.venv/bin/python -m nemotron super3 sft -c m1_agentic_smoke --dry-run \
  artifacts.wandb=false \
  artifacts.manifest.root=null
```

Result: PASS, `rc=0`, runtime 3s.
Log: `/tmp/nemotron-live-validation/task206/logs/04_sft_dry_run.log`.

Resolved dry-run evidence:
- Train script: `src/nemotron/recipes/super3/stage1_sft/test_train.py`.
- Packed data path:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`.
- Tokenizer path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- `training_contract.model_profile`: `qwen`.
- Checkpoint save path: `/tmp/nemotron-live-validation/task206/checkpoints`.
- `train.train_iters`: `1`.
- `checkpoint.save_interval`: `1`.

Resolver log:
`/tmp/nemotron-live-validation/task206/logs/05_resolved_config_probe.log`.

5. Conditional one-iteration smoke:

```bash
timeout 900 bash -lc 'PYTHONPATH=src \
NEMO_RUN_DIR=/tmp/nemotron-live-validation/task206 \
SUPER3_M1_AGENTIC_PACKED_DIR=/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits \
SUPER3_M1_TOKENIZER_MODEL=/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE=/tmp/nemotron-live-validation/task206/checkpoints \
/work-agents/.venv/bin/python -m nemotron super3 sft -c m1_agentic_smoke \
  artifacts.wandb=false \
  artifacts.manifest.root=null \
  train.train_iters=1 \
  checkpoint.save_interval=1'
```

Result: SKIPPED. Prerequisites were not all present.
Log: `/tmp/nemotron-live-validation/task206/logs/06_one_iter_smoke_skipped.log`.

6. Focused validators:

```bash
PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q \
  tests/recipes/super3/test_stage1_sft_train_bridge.py \
  tests/recipes/super3/test_sft_forward_step_dispatch.py \
  tests/recipes/super3/test_qwen_chat_contract.py \
  tests/recipes/super3/test_eval_chat_template_kwargs.py
```

Result: PASS, `33 passed, 2 skipped`, runtime 2s.
Log: `/tmp/nemotron-live-validation/task206/logs/07_sft_qwen_validators.log`.

## Artifacts

- Logs: `/tmp/nemotron-live-validation/task206/logs`.
- Checkpoint directory: `/tmp/nemotron-live-validation/task206/checkpoints`.
- No checkpoint files were created because the one-iteration smoke was skipped.

## Exact Resource Request

To run the task206 one-iteration local smoke, provide a single approved local or
project Python environment with:

- `torch` installed and importable.
- `megatron` installed and importable.
- `megatron.bridge` installed and importable.
- `nemo_run` installed and importable.
- At least one visible CUDA GPU, with either `nvidia-smi` available or
  `torch.cuda.is_available() == True` and `torch.cuda.device_count() >= 1`.
- Mounted Qwen model/tokenizer path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Packed Qwen splits, preferably
  `/tmp/nemotron-live-validation/task205/packed_qwen/splits`; fallback
  task071 splits are already available.

No package installation or cluster launch was performed for this task.

## Estimates

- Local one-iteration smoke after the exact resources above are available:
  15-45 minutes to rerun probes, dry-run, one train iteration, checkpoint write
  check, and evidence capture.
- Small SFT/eval pilot after resources are available: 30-90 minutes for local
  smoke plus checkpoint/eval-handoff metadata inspection; 2-6 wall-clock hours
  for a production-style limited-iteration 8-GPU pilot excluding queue time and
  endpoint/eval service setup.
- Full Qwen SFT training remains unmeasured locally; planning estimate is
  12-36 wall-clock hours on the intended multi-GPU allocation plus queue time,
  depending on final train-iter count, node count, checkpoint cadence, and eval
  handoff scope.
