# task103_sft_data_quality_strict_gate_s1 - Task Knowledge

<!-- METADATA:SESSION=12 -->

## Knowledge Entries

1. assignment: M1 Agentic SFT prep should have an opt-in strict gate for
   data-quality audit counters that were previously report-only.
2. implementation fact: strict mode checks five counters:
   `missing_required_source_metadata_count`, `duplicate_source_key_count`,
   `duplicate_normalized_prompt_hash_count`, `train_val_source_key_overlap_count`,
   and `train_val_normalized_prompt_overlap_count`.
3. behavioral contract: default prep remains report-only; callers must pass
   `--fail-on-data-quality-issues` to make nonzero audit counts fail the build.
4. diagnostic contract: strict failure writes manifest/report with checked counts
   before raising so operators can inspect the exact blocker.
