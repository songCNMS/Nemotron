# task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1 - task knowledge

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_2,SESSION=90 -->

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
6. Official worker_2 acceptance mailbox
   `intern_nemotron_worker_2_task341_acceptance_2ec935c4` confirms branch
   `origin/intern_nemotron_worker_2/task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1`
   at `2ec935c459b6d5953eb641d4ddc65fc247625288`. No task341 PR is visible yet;
   wait for a report/PR or blocker before assigning any training launch.
7. #404/task341 at head `8211c1397ef61fd3be6718d4e2bde1ca4c7728ab` is accepted
   as `BLOCK_TRAINING_READINESS` blocker closeout evidence only. The blocker is
   NemTron SSH route failure rc `255` / `connect failed: Connection refused`,
   independently reproduced by lead. This blocks live task-owned `/root` sync,
   task337 runtime validation, task298 checkpoint validation, and a defensible
   `nvidia_resiliency_ext` decision. Do not assign training until NemTron access
   is restored and task341 or an equivalent no-training handoff probe is rerun.
8. Lead gate was posted as PR comment `4622159239` because GitHub rejected
   formal same-author approval. Worker_2 may self-merge #404 only if exact head
   `8211c1397ef61fd3be6718d4e2bde1ca4c7728ab` remains `CLEAN`.
