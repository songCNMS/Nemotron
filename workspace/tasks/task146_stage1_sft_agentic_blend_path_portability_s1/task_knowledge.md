# task146_stage1_sft_agentic_blend_path_portability_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- `prepare_m1_agentic_sft._default_output_dir()` resolves to
  `${NEMO_RUN_DIR:-.}/output/super3/m1_agentic_sft_v0`.
- Stage1 SFT agentic consumer profiles should default `blend_path` to
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_agentic_sft_v0/data_blend_agentic_sft_v0.json`.
- Qwen-specific `tokenizer.model`, `chat_template`, `chat_template_kwargs`,
  `target_model_family`, and `config_name` are intentionally unchanged.
