# task136_lineage_publisher_relative_manifest_refs_s1 knowledge

<!-- METADATA:SESSION=4 -->

## Working Notes

- `maybe_publish_lineage_from_manifest()` knows the declaring manifest path,
  while `WandbArtifactPublisher.publish()` only receives a `LineageRecord`.
  Keeping the manifest-relative resolver in the helper avoids changing the
  public publisher API or lineage JSON contract.
- Custom `upstream_artifact_resolver` must remain authoritative. It should
  receive the original `LineageInput`, including the original relative ref.
- Publishing remains best-effort: malformed or missing upstream manifests
  should produce unresolved entries, and helper-level exceptions should still
  return `None` rather than crashing data prep.
