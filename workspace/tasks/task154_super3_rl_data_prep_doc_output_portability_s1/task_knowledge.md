# task154_super3_rl_data_prep_doc_output_portability_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- Super3 RL product docs should not include named-user `/mnt/3fs` output
  examples.
- M0 data-env examples should use
  `"${NEMO_RUN_DIR:-.}/output/super3/m0_data_env_foundation/smoke-20260516"`
  so they work outside a specific developer workspace.
