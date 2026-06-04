# task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1 - task knowledge

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

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
5. Acceptance base is current main
   `f16dffdef961b1a6cdb3ae23203f9ae7495b38ab`; lead docs came from
   `afbae9028daf7291d07db9a95f8d841b9981825f`.
6. task341 run `run_20260604T122328Z` is
   `BLOCK_TRAINING_READINESS` because SSH to configured `NemTron` fails with
   `connect failed: Connection refused`; this blocks required task-owned
   `/root` sync and live runtime/checkpoint validation.
7. task339 local checks still pass: artifact checksum `rc=0`, train-only shard
   checksum `rc=0`, and task339 disposition remains
   `PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME`.
8. Candidate checkpoint handoff is task298 iter0 root
   `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`,
   but task341 could not validate it live because NemTron is unreachable.
9. `nvidia_resiliency_ext` cannot be waived or remediated in task341 while
   NemTron is unreachable; keep it as an unresolved training-runtime blocker.
10. PR #404 was lead-approved as blocker evidence only at exact head
    `8211c1397ef61fd3be6718d4e2bde1ca4c7728ab` and merged at
    `2026-06-04T12:34:36Z` with merge commit
    `371aea491776cc258e1cbb59a081d28be0530438`. task310 launch/training,
    eval, export, endpoint, promotion, and AIME2025 train use remain not
    released.
