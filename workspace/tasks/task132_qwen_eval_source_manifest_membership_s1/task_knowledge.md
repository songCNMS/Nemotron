# task132_qwen_eval_source_manifest_membership_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- `validate_qwen_eval_repro_gate()` now derives a declared source-manifest set
  only after the top-level `source_manifests` list is non-empty and string-like.
- Evidence records still receive independent repo-relative path validation; the
  new membership check is additional lineage validation.
- The operator-facing membership issue names the offending
  `evidence_records[index].source_manifest` and says it is not declared in
  top-level `source_manifests`.
- Session 2 added no new task132 implementation knowledge; task133 applies the
  same membership pattern to benchmark-alignment evidence source manifests.
