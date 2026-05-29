# task143_m1_bridge_cli_output_dir_portability_s1 knowledge

<!-- METADATA:SESSION=6 -->

## Working Notes

- The M1 bridge consumers already point at `NEMO_RUN_DIR`-relative
  `output/super3/...` locations; this task aligns the producer CLI defaults.
- `build_parser()` now calls default-path helper functions, so parser
  construction after setting `NEMO_RUN_DIR` picks up the current run directory
  without affecting explicit CLI overrides.
- Session 6 added no new implementation knowledge; it only aligned durable
  bookkeeping with the open PR state.
