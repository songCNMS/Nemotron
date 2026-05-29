# task107_stage2_rl_bridge_manifest_val_holdout_s1 knowledge

<!-- METADATA:SESSION=13 -->

## Working Notes

- M1 SWE1, SWE2, and RLHF bridge manifests record split counts as mappings
  under `counts.train` and `counts.val`; summing `counts.val` gives the exact
  validation holdout for the bridge `combined.jsonl` artifact.
- `val_holdout: auto` is intentionally opt-in. Existing explicit integer
  holdout behavior remains available for manual/non-bridge JSONL inputs.
- Auto mode includes sibling manifest mtime/size and the inferred holdout in
  the split cache hash so a changed bridge manifest does not reuse a stale
  split.
- Auto mode rejects truncated sampling of a bridge combined JSONL because the
  bridge validation rows are at the end of the full file.
