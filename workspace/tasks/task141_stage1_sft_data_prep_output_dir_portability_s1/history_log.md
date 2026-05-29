# task141_stage1_sft_data_prep_output_dir_portability_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Read PM assignment for `task141_stage1_sft_data_prep_output_dir_portability_s1`.
- Created branch
  `intern_nem_dev_1/task141_stage1_sft_data_prep_output_dir_portability_s1`
  from `origin/main` at `b2aaf885220419038e6b01e7174c2ccd0c212da5`.
- Updated Stage1 SFT data-prep `default.yaml`, `tiny.yaml`,
  `agentic_v0.yaml`, and `qwen_agentic_v0.yaml` so `output_dir` uses
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/...`.
- Preserved blend paths, tokenizer/chat-template contracts,
  `used_in_filter` semantics, training configs, and launch commands.
- Added focused config tests covering literal `NEMO_RUN_DIR` defaults,
  `output/super3/` containment, profile suffix preservation, and OmegaConf
  resolution under a temp run directory.
- Verified focused Stage1 SFT config plus Qwen chat contract pytest,
  py_compile, Ruff, structured OmegaConf probe, and diff checks before opening
  the PR.
- Opened PR #248 to `main`: https://github.com/songCNMS/Nemotron/pull/248.
