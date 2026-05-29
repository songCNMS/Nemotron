# task144_stage3_eval_remote_job_dir_portability_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- Stage3 eval default `run.env.remote_job_dir` should be
  `${oc.env:NEMO_RUN_DIR,.}/.nemotron`.
- `execution.output_dir` intentionally remains
  `${run.env.remote_job_dir}/evaluations` so the evaluator output follows the
  same run root.
- The task intentionally does not change eval tasks, chat-template kwargs,
  benchmark classifications, mount mappings, deployment commands, route config,
  model artifact defaults, W&B config, cluster profile semantics, or live eval
  behavior.
