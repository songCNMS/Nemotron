# task335_qwen_all_sft_task333_30b_launch_preflight_s1 - task knowledge

<!-- METADATA:SESSION=3 -->

1. #396/task333 merged at `2026-06-04T08:37:16Z` via merge commit
   `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`.
2. Accepted packed root:
   `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`.
3. Target 30B model path:
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
4. task310 prior run is not `PASS_TRAINING`; validation hung and wrapper rc was
   nonzero. Future launch must preserve a safe validation/exit route.
5. This task is no-training/no-eval preflight only. It must not run optimizer
   steps, benchmark/AIME eval, export, endpoint, promotion, task255, AIME2025
   train rows, shared deletion, main push, merge, or self-merge.
6. Acceptance branch:
   `intern_nemotron_worker_2/task335_qwen_all_sft_task333_30b_launch_preflight_s1`
   from `origin/main` `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`; lead docs
   source `5c55be6227a01897adfec12231931ebe2eed7dbc`.
7. Before any NemTron remote/debug probe, current-main code must be synced to a
   task-owned `/root/task335_*` path. Do not run optimizer/training; only
   import/config/resource/data-path preflight is allowed.
8. Session 2 output root:
   `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z`.
9. The task-owned train-only view is the safe later launch data route:
   `84` train shards, `78,168` rows, `300,046,415` input tokens,
   `33,477,337` supervised tokens, and `0` valid/test shards. This preserves
   `do_validation=false` and avoids repeating the task310 validation hang route.
10. NemTron remote sync proof:
    `/root/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z/Nemotron`
    has synced head `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`.
11. Current exact launch blocker:
    `megatron.bridge.recipes.qwen.qwen3_moe` import fails with
    `ModuleNotFoundError("No module named 'megatron.energon'")`; this keeps the
    task at `BLOCK_LAUNCH_PREFLIGHT` and task310/all-SFT 30B training HOLD.
12. Passing subchecks: model path exists as `Qwen3MoeForCausalLM`,
    tokenizer chat template exists, Qwen packed/training pipeline contract
    passes on the train-only root, remote split exposure is train-only, and
    8 idle H200 GPUs are visible.
13. #398/task335 was approved as blocker-docs closeout only at exact head
    `0a094483458f01813b50e4fb13e2ddefdbdc4517` and merged at
    `2026-06-04T09:45:30Z` with merge commit
    `373d162d63a66f2dac6b94c43917be9c249cd83f`.
14. Next executable work is not training; it must be a separate lead-assigned
    runtime remediation for missing `megatron.energon`, followed by rerun or
    equivalent no-training preflight.
