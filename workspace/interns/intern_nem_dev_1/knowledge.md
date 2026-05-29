# intern_nem_dev_1 - 个人知识库

<!-- METADATA:SESSION=3 -->

---

## 知识条目

1. technical fact: Nano3 Stage3 eval default `run.env.remote_job_dir` should
   use `${oc.env:NEMO_RUN_DIR,.}/.nemotron`; `execution.output_dir` can remain
   `${run.env.remote_job_dir}/evaluations` so eval artifacts follow the run
   root.
