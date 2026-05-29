# task148_nano3_stage3_eval_remote_job_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Move Nano3 Stage3 eval `run.env.remote_job_dir` off checkout-relative
  `${oc.env:PWD}`.
- Use `${oc.env:NEMO_RUN_DIR,.}/.nemotron` while preserving
  `execution.output_dir: ${run.env.remote_job_dir}/evaluations`.
- Add focused static/OmegaConf coverage for raw and resolved paths.

## Boundaries

- Static/config/test/docs-only.
- No live eval/benchmark, endpoint calls, W&B, cluster jobs, data prep,
  training, artifact downloads, deploys, direct `main`/`master` push, or
  self-merge.

## Status

- Branch: `intern_nem_dev_1/task148_nano3_stage3_eval_remote_job_dir_portability_s1`
- Base: `311a407294be2de5413de3d300770b3c51afa986`
- PR: pending
