# task121_rlhf_pref_registry_revision_pins_s1 knowledge

<!-- METADATA:SESSION=17 -->

## Working Notes

- Required RLHF preference candidates can remain candidate rows, but their
  Hugging Face source revisions should still be pinned for lineage stability.
- `validate_data_registries.py --check-revision-pins --quiet` should now print
  the clean audit marker for live registries.
- Keep synthetic unpinned `pref_data_registry` rows informational so future
  exploration fixtures do not become production blockers.
