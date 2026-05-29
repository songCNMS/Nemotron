# task141_stage1_sft_data_prep_output_dir_portability_s1 knowledge

<!-- METADATA:SESSION=25 -->

## Working Notes

- Stage1 SFT data-prep YAML profiles should use
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/<profile-output-suffix>` for packed
  output portability.
- Preserved suffix mapping:
  `default -> stage1_sft`, `tiny -> stage1_sft_tiny`,
  `agentic_v0 -> stage1_sft_agentic_v0`, and
  `qwen_agentic_v0 -> stage1_sft_agentic_v0_qwen`.
- The task intentionally does not change blend inputs, tokenizer/chat-template
  contracts, `used_in_filter` semantics, training configs, or launch commands.
- Session 24 added no new implementation knowledge; it only aligned durable
  bookkeeping with the stop-hook requirement.
- PR #248 final tested head was `c6f955fb0f53f9b6d06e6b1024f7437d28ad7b2c`.
- PR #248 squash merged to `main` as
  `6013e06eed8277acc26229e5df95a256c6b5c3ee` after PM and independent test
  gates.
