# task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1 - task knowledge

<!-- METADATA:SESSION=2 -->

1. Accepted task335 blocker is missing `megatron.energon` when importing
   `megatron.bridge.recipes.qwen.qwen3_moe` on the NemTron route.
2. Current main for this task is
   `373d162d63a66f2dac6b94c43917be9c249cd83f`.
3. Any remediation must be no-training/no-eval and task-owned. It must not
   mutate shared roots or release task310.
4. PASS means import/runtime route proof only. It must be followed by a later
   no-training task335-equivalent preflight before any training launch task.
5. Acceptance branch:
   `intern_nemotron_worker_2/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1`
   from `origin/main` `373d162d63a66f2dac6b94c43917be9c249cd83f`; lead docs
   source `4fc5e1d3`.
6. Session 2 runtime target:
   `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`.
7. Runtime remediation PASS uses task-owned target installs only:
   `megatron-energon==7.3.2`, `multi-storage-client==0.49.0`,
   `xattr==1.3.0`, `wcmatch==10.1`, `bracex==2.6`,
   `braceexpand==0.1.7`, `rapidyaml==0.13.0.post2`,
   `deprecation==2.1.0`, `webdataset==1.0.2`, and `filetype==1.2.0`.
8. Final import proof passes for `megatron.energon` from the task-owned target
   and `megatron.bridge.recipes.qwen.qwen3_moe` from existing Megatron Bridge.
   This proves runtime import remediation only; a task335-equivalent
   no-training launch preflight rerun is still required before any training.
