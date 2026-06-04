# task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1 - task knowledge

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=88 -->

1. Accepted task335 blocker is missing `megatron.energon` when importing
   `megatron.bridge.recipes.qwen.qwen3_moe` on the NemTron route.
2. Current main for this task is
   `373d162d63a66f2dac6b94c43917be9c249cd83f`.
3. Any remediation must be no-training/no-eval and task-owned. It must not
   mutate shared roots or release task310.
4. PASS means import/runtime route proof only. It must be followed by a later
   no-training task335-equivalent preflight before any training launch task.
