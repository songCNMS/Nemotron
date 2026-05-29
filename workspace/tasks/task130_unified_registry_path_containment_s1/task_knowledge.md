# task130_unified_registry_path_containment_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- The production unified index lives under `data_registries/` but intentionally
  points at sibling milestone registry files such as `../m0_data_env/...`.
  Guarding strictly to the index directory would break the live registry.
- The containment rule therefore uses the parent milestones directory for
  indexes inside a `data_registries/` directory, and the index directory for
  other indexes.
- Inventory APIs return maps rather than issue lists, so invalid registry paths
  are skipped there after the same containment resolver rejects them. The
  validator remains the surface that reports clear path issues.
- Audit-only CLI modes bypass `validate_unified_index()` by design, so they
  must call the shared guarded loader directly. Invalid audit paths surface as
  CLI setup failures with exit code 2.
