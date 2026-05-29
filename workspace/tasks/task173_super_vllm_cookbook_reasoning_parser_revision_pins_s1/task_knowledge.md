# task173_super_vllm_cookbook_reasoning_parser_revision_pins_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- PM-provided parser revisions:
  - BF16: `d51eab0d1f979ebc26b546e634a04f450d99158e`
  - FP8: `7d7e5797b8a3c7abbab54033b6004e93e8b6bc91`
  - NVFP4: `4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6`
- Tests must parse the notebook JSON statically and must not run `wget`,
  `curl`, HF/model downloads, vLLM, endpoints, deploys, or artifact ops.

## Closeout Notes

- PR #280 merged into `main` at
  `5527046f0aeec3e37bf47b7b67f3b1b089164b4f`.
- PM merged-main verification passed the focused static notebook tests and
  probes; no live-serving or download knowledge was added.
