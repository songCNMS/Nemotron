# task138_stage2_rl_data_prep_output_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Align the generic Super3 Stage2 RL data-prep default YAML `output_dir` with
  the `RLDataPrepConfig` portability contract.
- Use a `NEMO_RUN_DIR`-relative `output/super3/stage2_rl_resolved` path.
- Preserve `tiny.yaml` and bridge consumer profile behavior.

## Boundaries

- Static/config/test-only.
- No live HF download, Stage2 RL data prep, RL training, eval, endpoint call,
  W&B, cluster job, artifact download, deployment, direct `main`/`master` push,
  or self-merge.

## Status

- Branch: `intern_nem_dev_1/task138_stage2_rl_data_prep_output_dir_portability_s1`
- Base: `70d3541cdbc993fa113bdc62fa9be61f83b72d9e`
- PR: https://github.com/songCNMS/Nemotron/pull/245
