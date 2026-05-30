# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Task224 must not run live endpoint, train, eval, benchmark, package
  install/build, model copy, or artifact upload operations.
- Use existing reports/logs/artifacts only.
- Required blockers to state explicitly: missing `nemo_evaluator_launcher`
  runtime, five M1 mapping gaps, M2 runtime assets/APIs/databases/sandboxes/
  baselines, and full benchmark PM re-release required.
- After task220/task223, the remaining blockers are benchmark-runner/coverage
  blockers rather than Qwen model/data/H200 availability blockers.
- Task220 proves 8-H200 full-data random-init one-iteration runtime,
  validation, checkpoint, and cleanup; it does not prove final trained-model
  quality because no pretrained Megatron checkpoint path was supplied.
