# task142_stage2_rl_data_prep_profile_output_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Scope

- Align remaining runnable/profile Stage2 RL data-prep YAML `output_dir`
  defaults with the `NEMO_RUN_DIR` run-directory contract.
- Preserve existing profile-specific suffixes under `output/super3/...`.
- Keep bridge `input_path` and `val_holdout: auto` behavior unchanged.
- Add focused static/config tests and an OmegaConf resolution probe.

## Boundaries

- Static config/test/docs only.
- No live HF dataset download, Stage2 RL/RLVR/SWE/RLHF data prep, RL
  training, eval, endpoint call, W&B run, cluster job, artifact download,
  deployment, direct `main`/`master` push, or self-merge.

## Status

- Branch:
  `intern_nem_dev_2/task142_stage2_rl_data_prep_profile_output_dir_portability_s1`
- Base: `494eb6d147dd4e3d5a7f959df3a5cb57fcfe77db`
- PR: Pending
