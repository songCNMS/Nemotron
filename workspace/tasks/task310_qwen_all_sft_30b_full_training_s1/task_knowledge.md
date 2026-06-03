# task310_qwen_all_sft_30b_full_training_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

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
