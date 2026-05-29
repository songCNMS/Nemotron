# task140_stage0_pretrain_data_prep_output_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Align Super3 Stage0 pretrain data-prep YAML `output_dir` defaults with the
  `data_prep.py` run-directory contract.
- Use `${oc.env:NEMO_RUN_DIR,.}/output/super3/...` for runnable data-prep
  profiles instead of `${oc.env:PWD}/../output/...`.
- Preserve existing per-profile output suffixes.
- Add focused static/config tests and an OmegaConf resolution probe.

## Boundaries

- Static/config/test-only.
- No live HF download, pretrain data prep, training, eval, endpoint call, W&B,
  cluster job, artifact download, deployment, direct `main`/`master` push, or
  self-merge.

## Status

- Branch:
  `intern_nem_dev_3/task140_stage0_pretrain_data_prep_output_dir_portability_s1`
- Base: `70d3541cdbc993fa113bdc62fa9be61f83b72d9e`
- PR: pending
