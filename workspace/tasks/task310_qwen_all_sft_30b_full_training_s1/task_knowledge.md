# task310_qwen_all_sft_30b_full_training_s1 - Task Knowledge

<!-- METADATA:SESSION=6 -->

## Knowledge Entries

1. The previous 30B FT checkpoint cannot be promoted or reused as success
   evidence because task306 scored `14/30`, below the accepted task300 base
   `15/30`.
2. The selected target is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` unless a
   task308/task309/runtime gate reports an exact blocker.
3. Full training must fail closed rather than downgrading to 4B or switching
   data/model paths silently.
4. As of Session 1, task308 branch
   `intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1`
   exists at `348cba44c02043cd6310a36ec722a68278288db2`, but no PR or
   `all_sft_pipeline_inventory_audit_report.md` PASS artifact is visible.
5. As of Session 1, task309 branch
   `intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
   exists at `d054925b1792a5365738247eeb8bdec462e1e6c6`, but no PR or
   `all_sft_packed_data_contract_report.md` PASS artifact is visible.
6. Task310 training must remain unlaunched until task308 and task309 have
   accepted PASS evidence and the current 30B runtime/resource assumptions are
   refreshed against the exact packed root.
7. Lead docs commit `5f4167dc` updated task310 to current `origin/main`
   `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122` and product-code baseline
   `ecb14173a820df377270273b9f7d9d92cb5076d2`; current lead docs head
   `9f838e94feccd0aad4b916dc8f29a6e4d0c80133` contains no additional task310
   file changes beyond that commit.
8. As of Session 3, task308 PR #374 is open/CLEAN at
   `f57384f6a298500f240a9367c3598cd5f9a59638` with
   `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`, which still requires a
   task309 packed-contract refresh before task310 launch.
9. As of Session 3, task309 PR #372 is open/CLEAN at
   `998ebce439164af2cc0e026575de32cd356acaa0`, but its report still records
   `BLOCK_DEPENDENCY_TASK308_INVENTORY_MISSING`; task310 remains HOLD until
   task309 refreshes from #374 and receives accepted `PASS_PACKED_CONTRACT`.
10. As of Session 4, task309 PR #372 is open/CLEAN at
    `fe1bb38c55545b54dc017647ae9f299ee1a5ac02` with report disposition
    `PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS`,
    but lead has not accepted it pending task312 refreshed review.
11. If task309 is accepted, task310 scope is constrained to the reviewed
    V11/task299 seed; generic `stage1_sft/data_blend_raw` remains NO-GO unless
    a separate materialized/count/decontam/Qwen-packing proof is accepted.
12. As of Session 5, task310 must not self-merge current #373 and must not
    refresh runtime/resources or launch training until #374, #372, and #375 are
    merged and lead authorizes the task310 next step.
13. As of Session 5, #374 is open/CLEAN at
    `a238cacb1f28fb96df58d3a10641a2b7325f61b7`, #372 is open/CLEAN at
    `4e26317adc536afc896377da9225913ca567135b`, and #375 is open/CLEAN at
    `a8a9ade370269daea0c38331c601dc38012b09be`; the required post-merge
    precondition is not met.
14. The constrained packed root for any lead-authorized task310 runtime refresh
    is
    `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`
    with model
    `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
15. As of Session 6, prerequisites #374/task308, #372/task309, and
    #375/task312 are merged into current main
    `004870e7d790778b5cdae5cc574257fdc19ec755`; task310 launch scope is only
    the constrained V11/task299 packed seed, and generic
    `stage1_sft/data_blend_raw` remains NO-GO.
16. Session 6 run roots are local
    `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`
    and remote
    `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`.
17. The task299 source and task-owned remote dereferenced mirror both have
    `391` files, `0` symlinks, and matching manifest sha256
    `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c`.
18. The bounded task310 launch used 8x H200, TP `4`, PP `2`, EP `4`, ETP `1`,
    `train_iters=35`, `global_batch_size=8`, `micro_batch_size=1`, `lr=5e-7`,
    `min_lr=1e-7`, `seed=5678`, and task298 pretrained checkpoint
    `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`.
19. Training reached `35/35` and saved checkpoint candidate
    `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`
    (`399G`, `28` files); `latest_checkpointed_iteration.txt` reads `35`.
20. Session 6 is not `PASS_TRAINING`: validation stopped making log progress
    at `Evaluating on 80 samples` / `Evaluating iter 1/10`, no `train_rc.txt`
    or `train_end.txt` existed as of `2026-06-03T16:26:54Z`, and processes
    remained alive. Lead decision is needed before termination/salvage handling.
