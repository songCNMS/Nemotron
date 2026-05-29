# task141_stage1_sft_data_prep_output_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Align Stage1 SFT data-prep YAML `output_dir` defaults with the
  `NEMO_RUN_DIR` portability contract.
- Keep generated packed-data outputs under `output/super3/`.
- Preserve per-profile suffixes for `default`, `tiny`, `agentic_v0`, and
  `qwen_agentic_v0`.

## Boundaries

- Static/config/test/docs-only.
- No live HF download, SFT data prep, SFT training, eval, endpoint call, W&B,
  cluster job, artifact download, deployment, direct `main`/`master` push, or
  self-merge.

## Status

- Branch: `intern_nem_dev_1/task141_stage1_sft_data_prep_output_dir_portability_s1`
- Base: `b2aaf885220419038e6b01e7174c2ccd0c212da5`
- PR: https://github.com/songCNMS/Nemotron/pull/248
