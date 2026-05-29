# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Production gate:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_eval_repro_gate.yaml`.
- Focused tests:
  `tests/recipes/super3/test_qwen_eval_repro_gate.py`.
- Remote raw artifact refs with `vm4vpn:` or `vpn:` must retain
  `remote_artifact_check.status: pm_verified`.
- Missing or non-file local raw artifact paths must continue to fail; do not
  relax `validate_raw_artifact_paths()`.
- Closeout: PR #291 merged and verified on `main` at
  `f74e7c05668f96766d10c730fcd14ddec7191350`; tested/merged replacement
  base/head were `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa` /
  `9456ed889081611380971457f2c579196f08390c`.
