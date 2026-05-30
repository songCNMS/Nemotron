# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Base commit: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_2/task206_qwen_sft_train_stack_unblock_probe_s1`.
- Evidence root: `/tmp/nemotron-live-validation/task206`.
- Required Qwen model path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Preferred fresh packed Qwen splits:
  `/tmp/nemotron-live-validation/task205/packed_qwen/splits`.
- Fallback packed Qwen splits:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`.
- One-iteration smoke may run only if `torch`, `megatron`,
  `megatron.bridge`, CUDA/GPU, Qwen model path, and packed Qwen splits are all
  present.
- Session 1 evidence:
  - `/work-agents/.venv/bin/python`: `nemo_run=True`, `torch=False`,
    `megatron=False`, `megatron.bridge=False`.
  - `conda`: not found.
  - Bounded alternate env inventory found no other usable project venv.
  - `nvidia-smi`: not found.
  - Qwen model path: absent.
  - Fresh task205 packed splits: absent.
  - Fallback task071 packed splits and blend: present.
  - Mandatory dry-run passed with `rc=0` in 3s.
  - Resolved train script:
    `src/nemotron/recipes/super3/stage1_sft/test_train.py`.
  - Resolved packed data path:
    `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`.
  - Resolved `training_contract.model_profile`: `qwen`.
  - Resolved checkpoint path:
    `/tmp/nemotron-live-validation/task206/checkpoints`.
  - One-iteration smoke skipped because prerequisites were missing.
  - Focused validators passed with `33 passed, 2 skipped`.
