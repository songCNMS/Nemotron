# task111_rlvr_bridge_manifest_val_holdout_auto_s1 knowledge

<!-- METADATA:SESSION=14 -->

## Working Notes

- RLVR uses `run_resolve_and_split()` with placeholder resolution, so
  `val_holdout: auto` must be resolved before the intermediate resolved JSONL
  becomes the final split input.
- Carrying the internal `_ValHoldoutResolution` into `split_local_jsonl()` keeps
  the final manifest source as `bridge_manifest` and avoids looking for a
  manifest beside the resolved intermediate file.
- Auto mode still rejects truncated `sample` runs for bridge combined JSONL
  because validation rows are at the end of the full bridge file.
