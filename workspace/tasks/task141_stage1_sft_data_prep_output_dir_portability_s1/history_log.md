# task141_stage1_sft_data_prep_output_dir_portability_s1 history

<!-- METADATA:SESSION=25 -->

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

## Session 24 - 2026-05-29

- Stop-hook audit required this task history to carry a Session 24 entry.
- Added Session 24 bookkeeping after PR #248 was already open and pushed.
- No product code, config, or test behavior changed in this session.

## Session 25 - 2026-05-29

- PM reported PR #248 merged after PM and independent test gates.
- Recorded final tested head `c6f955fb0f53f9b6d06e6b1024f7437d28ad7b2c`.
- Recorded squash merge/new main commit `6013e06eed8277acc26229e5df95a256c6b5c3ee`.
- PM merged-main checks passed: Stage1 SFT/Qwen config pytest 31 passed,
  py_compile, Ruff, structured OmegaConf probe, and `git diff --check`.
- Fetched `origin/main` and fast-forwarded local `main` to
  `6013e06eed8277acc26229e5df95a256c6b5c3ee`.
- No further task141 product action remains.
