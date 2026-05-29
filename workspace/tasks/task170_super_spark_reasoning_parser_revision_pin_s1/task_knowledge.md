# task170_super_spark_reasoning_parser_revision_pin_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- PM-provided metadata-only model revision:
  `4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6`.
- The pinned parser URL is:
  `https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4/resolve/4f0cf9daaeb7a4d5e23f80a00e7ed15f0e03caf6/super_v3_reasoning_parser.py`
- Tests must inspect the Spark guide statically and must not run `wget`, `curl`,
  HF/model downloads, vLLM, or TRT-LLM.

## Closeout Notes

- PR #277 merged into `main` at
  `3c1751adeea4eb26b7e6e8f41f9bb445ebc58f2d`.
- PM merged-main verification passed the focused Spark static test and probes;
  no additional live-serving knowledge was added.
