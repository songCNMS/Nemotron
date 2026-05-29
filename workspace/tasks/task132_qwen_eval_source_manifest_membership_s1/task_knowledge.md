# task132_qwen_eval_source_manifest_membership_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- `validate_qwen_eval_repro_gate()` now derives a declared source-manifest set
  only after the top-level `source_manifests` list is non-empty and string-like.
- Evidence records still receive independent repo-relative path validation; the
  new membership check is additional lineage validation.
- The operator-facing membership issue names the offending
  `evidence_records[index].source_manifest` and says it is not declared in
  top-level `source_manifests`.
