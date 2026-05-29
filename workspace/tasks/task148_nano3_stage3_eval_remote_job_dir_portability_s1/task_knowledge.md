# task148_nano3_stage3_eval_remote_job_dir_portability_s1 knowledge

<!-- METADATA:SESSION=3 -->

## Working Notes

- Nano3 Stage3 eval default `run.env.remote_job_dir` should be
  `${oc.env:NEMO_RUN_DIR,.}/.nemotron`.
- `execution.output_dir` intentionally remains
  `${run.env.remote_job_dir}/evaluations` so evaluator output follows the run
  root.
- This task intentionally does not change task baskets, chat-template kwargs,
  tokenizer fields, OpenAI routes, deployment shape, launch command semantics,
  or live-run surfaces.
