# task142_stage2_rl_data_prep_profile_output_dir_portability_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- Generic Stage2 RL data-prep `default.yaml` was already portable from PR
  #245; this task covers the remaining runnable/profile configs only.
- The Stage2 RL profile suffixes are preserved:
  `stage2_rl_tiny`, `stage2_rl/rlvr1`, `stage2_rl/rlvr2`,
  `stage2_rl/rlvr3`, `stage2_rl/swe1`, `stage2_rl/swe2`, and
  `stage2_rl/rlhf`.
- Bridge consumers should keep `input_path` pointing at
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/.../combined.jsonl` and
  `val_holdout: auto`.
