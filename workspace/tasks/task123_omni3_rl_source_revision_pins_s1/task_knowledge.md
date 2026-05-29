# task123_omni3_rl_source_revision_pins_s1 knowledge

<!-- METADATA:SESSION=19 -->

## Working Notes

- Keep `source_uri` and `source_revision` separate in Omni3 data-prep configs;
  this preserves existing URI readability while making the source pin explicit.
- RL-Omni cache identity should include source URI and source revision so a
  source pin change cannot reuse a run directory created for a different
  upstream snapshot.
- `DataBlend.Dataset.revision` is optional for backward compatibility; Omni3
  text RL validates the configured `source_revision` against matching blend
  dataset revisions when a source pin is configured.
- A pinned Omni3 text source must have at least one blend row whose `path`
  equals `cfg.source_uri`; otherwise a source URI typo can skip revision
  comparison entirely.
