# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Production gate:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_eval_repro_gate.yaml`.
- Focused tests:
  `tests/recipes/super3/test_qwen_eval_repro_gate.py`.
- Remote raw artifact refs with `vm4vpn:` or `vpn:` must retain
  `remote_artifact_check.status: pm_verified`.
- Missing or non-file local raw artifact paths must continue to fail; do not
  relax `validate_raw_artifact_paths()`.
