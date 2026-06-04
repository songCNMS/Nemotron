# task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1 - task knowledge

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=90 -->

1. #402/task339 merged no-training preflight evidence at
   `2026-06-04T12:07:41Z`, merge commit
   `f16dffdef961b1a6cdb3ae23203f9ae7495b38ab`.
2. task339 artifact root:
   `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`.
3. This task is not training. It must resolve or explicitly gate
   `nvidia_resiliency_ext`, verify checkpoint handoff, and render exact launch
   placeholders before any optimizer step can be considered.
4. The target remains Qwen3-30B-A3B-Instruct at
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`; no 4B
   downgrade or checkpoint switch is allowed.
