# task100_qwen_scaleup_train_model_ref_contract_s1 knowledge

<!-- METADATA:SESSION=12 -->

## Working Notes

- `build_manifest()` stores the train model path under
  `manifest["training"]["qwen_hf_model"]` and the tokenizer path under
  `manifest["packing"]["tokenizer_model"]`.
- `render_remote_train_script()` already exports both
  `SUPER3_M1_QWEN_HF_MODEL` and `SUPER3_M1_TOKENIZER_MODEL`; only the torchrun
  `training_contract.model_ref` override needed to align with the model export.
- The focused regression is the distinct path case:
  `/remote/models/Qwen3-30B-A3B-Instruct-2507` must be the model ref, while
  `/local/models/Qwen3-30B-A3B-Instruct-2507` remains only the tokenizer ref.
- Session 12 adds no new task100-specific implementation knowledge; task101
  carries the direct M1 planner analogue.
