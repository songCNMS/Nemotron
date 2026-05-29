# task140_stage0_pretrain_data_prep_output_dir_portability_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Created branch
  `intern_nem_dev_3/task140_stage0_pretrain_data_prep_output_dir_portability_s1`
  from `origin/main` at `70d3541cdbc993fa113bdc62fa9be61f83b72d9e`.
- Updated Stage0 pretrain data-prep YAML `output_dir` defaults to use
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/...`.
- Added focused config tests for static defaults and OmegaConf resolution under
  a temporary `NEMO_RUN_DIR`.
- Verified focused pytest, py_compile, Ruff, structured OmegaConf probe, and
  diff checks before staging.
- Opened PR #247 to `main`: https://github.com/songCNMS/Nemotron/pull/247.
