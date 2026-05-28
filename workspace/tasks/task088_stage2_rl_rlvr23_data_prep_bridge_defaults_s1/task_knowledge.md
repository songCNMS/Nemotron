# task088_stage2_rl_rlvr23_data_prep_bridge_defaults_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. assignment: RLVR2/RLVR3 data-prep defaults must consume M1 RLVR bridge `combined.jsonl` outputs instead of developer-local release JSONL files.
2. technical fact: `prepare_m1_rlvr_jsonl.py --mix rlvr2` and `--mix rlvr3` are the bridge entry points for mix-specific train/val/combined outputs plus manifest/report/fingerprint lineage.
3. technical fact: RLVR3 currently has no active registry rows, but its data-prep default should still encode the intended bridge contract rather than a runnable local file bypass.
4. test contract: all three RLVR data-prep defaults should reject `/lustre/` and `yifuw`, include `combined.jsonl`, include the correct `m1_rlvr/<mix>` directory, and keep `_data_prep_base` fields.
