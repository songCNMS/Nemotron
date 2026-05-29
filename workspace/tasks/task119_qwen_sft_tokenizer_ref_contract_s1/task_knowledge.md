# task119_qwen_sft_tokenizer_ref_contract_s1 knowledge

<!-- METADATA:SESSION=19 -->

## Working Notes

- `validate_qwen_data_prep_config()` now uses `_is_qwen_ref()` after the
  explicit Nemotron/Super3 default check. Qwen data prep therefore rejects
  non-Qwen tokenizer refs before any SFT packing can produce wrong-tokenizer
  rows.
- The production `qwen_agentic_v0.yaml` profile still validates when
  `SUPER3_M1_TOKENIZER_MODEL` is set separately from
  `SUPER3_M1_QWEN_HF_MODEL`, and when it falls back to
  `SUPER3_M1_QWEN_HF_MODEL`.
- `validate_qwen_packed_sft_chat_contract()` now treats `tokenizer_uri` as
  required lineage when a training tokenizer is supplied, and rejects present
  tokenizer URIs that are not recognizably Qwen even without a training
  tokenizer argument.
