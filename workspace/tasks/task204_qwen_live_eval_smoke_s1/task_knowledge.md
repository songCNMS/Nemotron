# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Required base: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Task artifacts root: `/tmp/nemotron-live-validation/task204`.
- Required dry-run command:
  `PYTHONPATH=src /work-agents/.venv/bin/python -m nemotron super3 eval -c m1_corrected_math_comparison --dry-run run.model=qwen-live-validation-smoke execution.type=local deployment.type=generic deployment.url=http://127.0.0.1:13000/v1/chat/completions`.
- Required validator shard:
  `tests/recipes/super3/test_qwen_eval_repro_gate.py`,
  `tests/recipes/super3/test_benchmark_alignment_path_guards.py`,
  `tests/recipes/super3/test_m1_eval_full_basket.py`,
  `tests/recipes/super3/test_m2_eval_basket_s1.py`,
  `tests/recipes/super3/test_m2_eval_basket_s2.py`.
- Evidence artifacts:
  - `/tmp/nemotron-live-validation/task204/dry_run/m1_corrected_math_comparison_dry_run_timed.log`
  - `/tmp/nemotron-live-validation/task204/validators/qwen_m1_m2_validators_timed.log`
  - `/tmp/nemotron-live-validation/task204/endpoint_smoke/availability_probe_sanitized.json`
  - `/tmp/nemotron-live-validation/task204/endpoint_smoke/endpoint_smoke_sanitized.json`
  - `/tmp/nemotron-live-validation/task204/task204_evidence_summary.md`
  - `/tmp/nemotron-live-validation/task204/task204_evidence_summary.json`
