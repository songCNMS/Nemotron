# task144_stage3_eval_remote_job_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Move Stage3 eval `run.env.remote_job_dir` off checkout-relative `${oc.env:PWD}`.
- Use `${oc.env:NEMO_RUN_DIR,.}/.nemotron` while preserving
  `execution.output_dir: ${run.env.remote_job_dir}/evaluations`.
- Add focused static/OmegaConf coverage for raw and resolved paths.

## Boundaries

- Static/config/test/docs-only.
- No live benchmark/eval run, endpoint call, W&B run, cluster job, data prep,
  training, artifact download, deployment, direct `main`/`master` push, or
  self-merge.

## Status

- Branch: `intern_nem_dev_1/task144_stage3_eval_remote_job_dir_portability_s1`
- Base: `802f7bee98579e5a9647813f5182bb048e1aa44b`
- PR: https://github.com/songCNMS/Nemotron/pull/251
