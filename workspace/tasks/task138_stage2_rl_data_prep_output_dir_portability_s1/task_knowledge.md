# task138_stage2_rl_data_prep_output_dir_portability_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- `RLDataPrepConfig.output_dir` defaults to
  `Path(os.environ.get("NEMO_RUN_DIR", ".")) / "output/super3/stage2_rl_resolved"`.
- Generic Stage2 RL data-prep `default.yaml` should use the same portable
  `NEMO_RUN_DIR` fallback and stay inside the `output/super3/` namespace.
- The task intentionally leaves `tiny.yaml` and bridge consumer profiles
  unchanged.
