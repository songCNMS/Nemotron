# task140_stage0_pretrain_data_prep_output_dir_portability_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- `src/nemotron/recipes/super3/stage0_pretrain/data_prep.py` already uses
  `NEMO_RUN_DIR` through `_OUTPUT_BASE`; the YAML profiles needed matching
  `output_dir` defaults.
- Existing Stage0 pretrain data-prep profile suffixes are preserved:
  `stage0_pretrain/phase1`, `stage0_pretrain/phase2`,
  `stage0_pretrain/long_context`, and `stage0_pretrain_tiny`.
