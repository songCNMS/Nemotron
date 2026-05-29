# intern_nem_dev_1 - 个人知识库

<!-- METADATA:SESSION=27 -->

---

## 知识条目

1. technical fact: Stage3 eval default `run.env.remote_job_dir` should follow
   `${oc.env:NEMO_RUN_DIR,.}/.nemotron`; `execution.output_dir` can remain
   `${run.env.remote_job_dir}/evaluations` so eval artifacts stay under the run
   root.
