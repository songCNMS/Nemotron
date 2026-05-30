# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Base commit: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_2/task203_qwen_live_sft_train_smoke_s1`.
- Evidence root: `/tmp/nemotron-live-validation/task203`.
- Preferred fresh packed Qwen input:
  `/tmp/nemotron-live-validation/task202/packed_qwen/splits`.
- Existing fallback packed Qwen input:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`.
- Existing fallback blend:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/blend.json`.
- Qwen tokenizer/model path requested by PM:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Dry-run command must set `SUPER3_M1_TRAINING_PROFILE=qwen`,
  `artifacts.wandb=false`, and `artifacts.manifest.root=null`.
- Session 1 evidence:
  - Dry-run passed with `rc=0` in 3s.
  - Resolved train script:
    `src/nemotron/recipes/super3/stage1_sft/test_train.py`.
  - Resolved packed data path:
    `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/packed_qwen/splits`.
  - Resolved tokenizer path:
    `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
  - Resolved `training_contract.model_profile`: `qwen`.
  - Resolved checkpoint save path:
    `/tmp/nemotron-live-validation/task203/checkpoints`.
  - Focused validators passed with `33 passed, 2 skipped`.
  - Live one-iteration smoke was skipped because `torch`, `megatron`, and
    `megatron.bridge` are not installed/importable in `/work-agents/.venv`, the
    requested Qwen path is absent, and CUDA availability cannot be established.
- Session 2 handoff: PM created follow-up
  `task206_qwen_sft_train_stack_unblock_probe_s1` specifically to inventory
  local/project Python environments and GPU/model resources before deciding
  whether the one-iteration smoke can run.
