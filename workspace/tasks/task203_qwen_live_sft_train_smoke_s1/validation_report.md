# Task203 Validation Report

<!-- METADATA:SESSION=1 -->

## Summary

- Owner: `intern_nem_dev_2`.
- Base commit: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_2/task203_qwen_live_sft_train_smoke_s1`.
- Evidence root: `/tmp/nemotron-live-validation/task203`.
- Result: dry-run and focused validators passed; one-iteration local smoke was
  blocked by missing local training dependencies/resources.

## Commands And Results

1. Input artifact probe:

```bash
test -d /tmp/nemotron-live-validation/task202/packed_qwen/splits || true
test -d /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits
test -f /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/blend.json
test -d /mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507 || true
```

Result: task202 fresh splits absent; fallback splits `rc=0`; fallback
`blend.json` `rc=0`; requested `/mnt/3fs` Qwen model path absent.
Log: `/tmp/nemotron-live-validation/task203/logs/01_input_probe.log`.

2. SFT profile compile dry-run:

```bash
PYTHONPATH=src \
NEMO_RUN_DIR=/tmp/nemotron-live-validation/task203 \
SUPER3_M1_AGENTIC_PACKED_DIR=/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits \
SUPER3_M1_TOKENIZER_MODEL=/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE=/tmp/nemotron-live-validation/task203/checkpoints \
/work-agents/.venv/bin/python -m nemotron super3 sft -c m1_agentic_smoke --dry-run \
  artifacts.wandb=false \
  artifacts.manifest.root=null
```

Result: PASS, `rc=0`, runtime 3s.
Log: `/tmp/nemotron-live-validation/task203/logs/02_sft_dry_run.log`.

Dry-run/config evidence:
- Train script: `src/nemotron/recipes/super3/stage1_sft/test_train.py`.
- Packed data path:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`.
- Tokenizer path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- `training_contract.model_profile`: `qwen`.
- Checkpoint save path: `/tmp/nemotron-live-validation/task203/checkpoints`.
- `train.train_iters`: `1`.
- `checkpoint.save_interval`: `1`.
Resolver log:
`/tmp/nemotron-live-validation/task203/logs/03_resolved_config_probe.log`.

3. Dependency/CUDA probe:

```bash
PYTHONPATH=src /work-agents/.venv/bin/python - <<'PY'
import importlib.util
import torch
mods = ["megatron", "megatron.bridge", "nemo_run"]
for mod in mods:
    print(f"{mod}: {bool(importlib.util.find_spec(mod))}")
print(f"torch_cuda_available: {torch.cuda.is_available()}")
print(f"torch_cuda_device_count: {torch.cuda.device_count()}")
PY
```

Result: FAIL, `rc=1`, runtime 0s, because `torch` is not installed in
`/work-agents/.venv`.
Log: `/tmp/nemotron-live-validation/task203/logs/04_dependency_cuda_probe.log`.

Supplemental safe import-spec probe:
- `torch: False`
- `megatron: False`
- `megatron.bridge: False`
- `nemo_run: True`

Log:
`/tmp/nemotron-live-validation/task203/logs/04c_dependency_spec_probe_safe.log`.

4. One-iteration local smoke:

```bash
timeout 900 bash -lc 'PYTHONPATH=src \
NEMO_RUN_DIR=/tmp/nemotron-live-validation/task203 \
SUPER3_M1_AGENTIC_PACKED_DIR=/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits \
SUPER3_M1_TOKENIZER_MODEL=/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_SFT_SMOKE_SAVE=/tmp/nemotron-live-validation/task203/checkpoints \
/work-agents/.venv/bin/python -m nemotron super3 sft -c m1_agentic_smoke \
  artifacts.wandb=false \
  artifacts.manifest.root=null \
  train.train_iters=1 \
  checkpoint.save_interval=1'
```

Result: SKIPPED. Required conditions were not met: `torch`, `megatron`, and
`megatron.bridge` are missing, the requested `/mnt/3fs` Qwen model path is
absent, and CUDA availability cannot be established without `torch`.
Log: `/tmp/nemotron-live-validation/task203/logs/05_one_iter_smoke_skipped.log`.

5. Focused SFT/Qwen validators:

```bash
PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q \
  tests/recipes/super3/test_stage1_sft_train_bridge.py \
  tests/recipes/super3/test_sft_forward_step_dispatch.py \
  tests/recipes/super3/test_qwen_chat_contract.py \
  tests/recipes/super3/test_eval_chat_template_kwargs.py
```

Result: PASS, `33 passed, 2 skipped`, runtime 3s.
Log: `/tmp/nemotron-live-validation/task203/logs/06_sft_qwen_validators.log`.

## Artifact Paths

- Logs: `/tmp/nemotron-live-validation/task203/logs`.
- Checkpoint directory: `/tmp/nemotron-live-validation/task203/checkpoints`.
- No checkpoint files were created because the one-iteration smoke was skipped.

## Blockers

- `/work-agents/.venv` lacks `torch`.
- `/work-agents/.venv` lacks `megatron`.
- `/work-agents/.venv` lacks `megatron.bridge`.
- Requested model/tokenizer path is absent:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- CUDA availability and device count could not be established because `torch`
  is missing.

## Estimates

- Small local SFT/eval pilot after dependencies, GPU, and model path are
  available: 30-90 minutes for environment startup, dry-run, a 1-10 iteration
  local smoke, checkpoint write check, and metadata/eval-handoff inspection.
- Small production-style pilot using the real `m1_agentic_train` path and a
  limited train-iter override: 2-6 wall-clock hours on a suitable single
  8-GPU node, excluding queue time and endpoint/eval service setup.
- Full Qwen SFT training estimate cannot be measured from this local environment;
  planning estimate is 12-36 wall-clock hours on the intended multi-GPU
  allocation plus queue time, with exact duration depending on final
  train-iter count, node count, checkpoint cadence, and eval handoff scope.
