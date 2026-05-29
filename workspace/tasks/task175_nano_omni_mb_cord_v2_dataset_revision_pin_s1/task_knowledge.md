# task175_nano_omni_mb_cord_v2_dataset_revision_pin_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- PM-provided CORD-v2 revision:
  `7f0115a4b758a71d6473b8d085751692da2fef98`.
- Tests must parse the notebook JSON statically and must not execute the
  notebook, call `load_dataset`, download from Hugging Face, train, or touch
  endpoints, W&B, cluster, deploy, or artifact operations.

## Session 2 Notes

- The notebook contains bash and Python cells, so focused AST tests should
  parse only Python cells that contain the target CORD-v2 `load_dataset` call.
