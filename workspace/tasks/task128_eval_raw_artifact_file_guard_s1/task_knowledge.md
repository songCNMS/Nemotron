# task128_eval_raw_artifact_file_guard_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- `benchmark_alignment.py` imports and reuses
  `qwen_eval_repro_gate.validate_raw_artifact_paths()`, so tightening the
  shared helper covers both validation surfaces.
- The fingerprint helper deliberately hashes only regular local files; rejecting
  non-file raw paths before fingerprint comparison prevents directories from
  passing with arbitrary 64-character hex strings.
- Remote `vm4vpn:` and `vpn:` references still bypass local filesystem checks
  and rely on the caller's PM-verified metadata validation.
