# task112_benchmark_alignment_local_artifact_fingerprint_s1 knowledge

<!-- METADATA:SESSION=15 -->

## Working Notes

- `validate_local_raw_artifact_fingerprints()` is now exported from
  `qwen_eval_repro_gate.py` and reused by `benchmark_alignment.py`.
- The helper only applies to local raw artifact paths. Remote `vm4vpn:` and
  `vpn:` refs still rely on PM-verified artifact metadata.
- Current `qwen_benchmark_alignment_ledger.yaml` evidence records are
  remote-only, so no ledger metadata change was required.
