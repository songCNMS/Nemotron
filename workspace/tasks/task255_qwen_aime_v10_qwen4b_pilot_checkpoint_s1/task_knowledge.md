# task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. task255 is the first checkpoint/export artifact production task after
   task253/task254 approved local Qwen3-4B packed shards.
2. The accepted same-harness Qwen3-4B base score remains `11/30`.
3. task255 must not run task243 comparison or make promotion claims; it only
   produces candidate FT artifacts or a precise blocker.
4. If using `NemTron`, code must be synced to `/root` before debug/training.
5. No 30B/8-GPU scale is allowed in this task.
6. Base branch for task255 is `origin/main` after #328 merge commit
   `61fa65e9e9a535d531a65072c839760c3488207f`; lead docs source is
   `origin/intern_nemotron_lead/session1-recovery-task-docs`
   `9a32856af7b1676e02e2be296e01e03d68da5c15`.
7. For `qwen_local_train.py`, planner-emitted `training_contract.*` CLI
   overrides can fail after the script config is merged into the Megatron
   `ConfigContainer` because that container is struct-typed and does not keep a
   `training_contract` section. The successful task255 launch used the Qwen
   contract through environment variables and omitted those redundant CLI
   overrides.
8. task255 produced a bounded Qwen3-4B candidate artifact pair on NemTron:
   Megatron torch_dist checkpoint
   `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/checkpoints_retry_no_training_contract_cli`
   and HF export
   `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
   These artifacts still require independent review and task243 same-harness
   comparison before any quality judgment.
