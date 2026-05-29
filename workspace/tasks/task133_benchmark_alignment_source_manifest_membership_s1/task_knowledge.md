# task133_benchmark_alignment_source_manifest_membership_s1 knowledge

<!-- METADATA:SESSION=3 -->

## Working Notes

- Benchmark alignment now distinguishes result manifests from other repo YAMLs
  by declaring an explicit top-level `source_manifests` allowlist.
- Evidence source manifests still use `_validate_repo_relative_existing_paths()`
  for absolute/traversal/symlink/missing/directory protection; membership is an
  additional lineage check.
- `qwen_eval_repro_gate.yaml` and `qwen_benchmark_alignment_ledger.yaml` are
  existing repo YAMLs but are not result manifests and must not count as
  evidence source manifests.
- Session 2 added no new implementation knowledge; it only records stop-hook
  bookkeeping after PR #240 opened.
- Session 3 added no new task133 implementation knowledge; task133 is merged
  and task137 starts from the merged main base.
