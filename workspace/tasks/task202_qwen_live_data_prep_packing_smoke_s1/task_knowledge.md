# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task202 is evidence-only unless a concrete bug is found.
- The task071 Qwen M1 SFT blend is:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/data_blend_agentic_sft_v0.json`.
- The task071 source manifest is:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/manifest.json`.
- The requested Qwen tokenizer/model resource path is:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- If that model path is absent, the PM instruction says to record it as a
  tokenizer/model resource blocker and still run the dry-run plus static
  validators.
- The qwen_agentic_v0 data-prep config defaults to `num_shards=16`,
  `pack_size=4096`, and tokenizer-template Qwen packing.
