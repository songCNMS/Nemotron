# task101_qwen_m1_training_plan_model_ref_contract_s1 history

<!-- METADATA:SESSION=12 -->

## Session 12 - 2026-05-28

- Synced local `main` to
  `944483ba510fd4a8b98bf00613127567a499f8dc` and created branch
  `intern_nem_dev_3/task101_qwen_m1_training_plan_model_ref_contract_s1`.
- Added direct M1 planner support for `--qwen-hf-model` with
  `SUPER3_M1_QWEN_HF_MODEL` env fallback and tokenizer fallback for legacy Qwen
  manifests.
- Changed Qwen direct training plans so `training_contract.model_ref` uses the
  resolved Qwen HF model path instead of the tokenizer path.
- Updated generated Qwen run scripts to export `SUPER3_M1_QWEN_HF_MODEL` while
  preserving `SUPER3_M1_TOKENIZER_MODEL`.
- Added focused assertions for separate Qwen HF model and tokenizer paths.
- Verified focused planner pytest, py_compile, Ruff, structured rendered
  manifest/script probe, and `git diff --check`.
- Opened PR #209 to `main`: https://github.com/songCNMS/Nemotron/pull/209.
- Confirmed no live train/eval runs, endpoints, W&B, cluster jobs, deployment,
  promotion, direct `main` or `master` push, or self-merge was performed.
