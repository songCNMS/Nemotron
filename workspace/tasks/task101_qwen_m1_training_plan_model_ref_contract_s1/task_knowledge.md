# task101_qwen_m1_training_plan_model_ref_contract_s1 knowledge

<!-- METADATA:SESSION=12 -->

## Working Notes

- Direct M1 planner tokenizer resolution remains `infer_tokenizer_model()` from
  metadata or `--tokenizer-model`; this path should not become the model
  lineage field when a distinct Qwen HF model is provided.
- `qwen_model_ref_for_training()` returns `None` for non-Qwen profiles, so
  legacy Nemotron manifests keep `training_contract.model_ref` unset.
- For Qwen profiles, model ref precedence is `--qwen-hf-model`,
  `SUPER3_M1_QWEN_HF_MODEL`, then tokenizer fallback for older manifests.
- `render_run_script()` exports `SUPER3_M1_QWEN_HF_MODEL` only when the
  training profile is Qwen and a model ref is available.
