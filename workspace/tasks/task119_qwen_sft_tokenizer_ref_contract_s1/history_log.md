# task119_qwen_sft_tokenizer_ref_contract_s1 history

<!-- METADATA:SESSION=19 -->

## Session 18 - 2026-05-29

- Synced local `main` to
  `259938c631c64bd6beef1ef08d55080e12d37fe6` and created branch
  `intern_nem_dev_3/task119_qwen_sft_tokenizer_ref_contract_s1`.
- Reused the existing Qwen reference detection helper in
  `validate_qwen_data_prep_config()` so `/models/Llama-3-tokenizer` and other
  non-Qwen tokenizer refs fail during data-prep validation.
- Added focused tests for accepted Qwen HF IDs, rejected non-Qwen tokenizer
  refs, production `qwen_agentic_v0` env-resolved cases, and legacy Super3
  data-prep configs remaining explicit non-Qwen profiles.
- Verified focused pytest, py_compile, Ruff, structured validator probe, and
  `git diff --check` before staging.
- PR: pending.

## Session 19 - 2026-05-29

- Incorporated the PM addendum on the same task119 branch before opening a PR.
- Hardened `validate_qwen_packed_sft_chat_contract()` so calls with a training
  `tokenizer_model` require non-empty packed metadata `tokenizer_uri`.
- Added Qwen lineage validation for packed metadata `tokenizer_uri`, rejecting
  non-Qwen values even when no training tokenizer is supplied.
- Added focused tests and structured probe coverage for missing
  `tokenizer_uri`, non-Qwen `tokenizer_uri`, and valid local path, `file://`,
  `https://huggingface.co/Qwen/...`, and `hf://models/Qwen/...` normalization
  cases.
- Re-verified focused pytest, py_compile, Ruff, structured validator probe,
  and `git diff --check` before staging.
- PR: pending.
