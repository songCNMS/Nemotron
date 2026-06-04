# task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1 - task knowledge

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_2,SESSION=90 -->

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
5. Worker_2 accepted task341 locally at `2026-06-04T12:15:16Z` on branch
   `intern_nemotron_worker_2/task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1`
   from `origin/main` `f16dffdef961b1a6cdb3ae23203f9ae7495b38ab`, with lead
   docs imported from `afbae9028daf7291d07db9a95f8d841b9981825f`. At lead
   observation time there was no task341 remote branch or PR yet, so this is
   acceptance/Working evidence only.
