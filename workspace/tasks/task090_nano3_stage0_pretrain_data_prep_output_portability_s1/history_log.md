# task090_nano3_stage0_pretrain_data_prep_output_portability_s1 - History Log

<!-- METADATA:SESSION=14 -->

## Session 14 - 2026-05-28

- Received PM assignment to fix Nano3 stage0 pretrain data-prep default output
  portability.
- Fast-forwarded local `main` to
  `c26dedfcbff336e3f827f59f39230d713d260e29` and created branch
  `intern_nem_dev_1/task090_nano3_stage0_pretrain_data_prep_output_portability_s1`.
- Updated `default.yaml` `output_dir` from the named-user `/lustre` path to
  `${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain`.
- Left `tiny.yaml` unchanged because it already uses a portable relative output
  path and preserves the tiny sample/force behavior.
- Added `tests/recipes/nano3/stage0_pretrain/test_data_prep_config_defaults.py`
  to validate required Nano3 stage0 pretrain data-prep fields, output-dir
  portability, and the default path contract.
- Validation passed locally: focused pytest shard, py_compile, Ruff, static
  output_dir scan, `git diff --check`, and `git diff --cached --check`.
- Opened PR #197 to `main`: https://github.com/songCNMS/Nemotron/pull/197.
