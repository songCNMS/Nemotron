# task119_qwen_sft_tokenizer_ref_contract_s1

## Scope

- Harden `validate_qwen_data_prep_config()` so Qwen-target data prep rejects
  tokenizer refs that are not recognizably Qwen.
- Preserve valid Qwen HF IDs and local paths containing `Qwen`.
- Preserve separate `SUPER3_M1_TOKENIZER_MODEL` /
  `SUPER3_M1_QWEN_HF_MODEL` behavior.
- Preserve legacy explicit Super3 data-prep configs as non-Qwen profiles.
- Require packed Qwen SFT metadata to record a non-empty `tokenizer_uri` when
  a training `tokenizer_model` is supplied, and reject non-Qwen
  `tokenizer_uri` values even when no training tokenizer is supplied.
- Preserve tokenizer URI normalization for local paths, `file://`,
  `https://huggingface.co/Qwen/...`, and `hf://models/Qwen/...` refs.

## Boundaries

- No live SFT packing, data prep, training launch, checkpoint conversion,
  endpoint call, W&B run, cluster job, deployment, direct `main`/`master` push,
  or self-merge.

## Status

- Branch: `intern_nem_dev_3/task119_qwen_sft_tokenizer_ref_contract_s1`
- Base: `259938c631c64bd6beef1ef08d55080e12d37fe6`
- PR: pending
