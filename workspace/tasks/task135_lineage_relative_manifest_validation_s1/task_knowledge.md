# task135_lineage_relative_manifest_validation_s1 knowledge

<!-- METADATA:SESSION=3 -->

## Working Notes

- Public `walk_chain()` should continue returning `list[LineageRecord]`.
  Validation needs the declaring manifest path, so the implementation uses an
  internal path-preserving walker and adapts public output from it.
- Relative manifest refs must be resolved from the manifest that declares the
  input, not from the process working directory.
- Absolute manifest refs remain supported by the module contract.
