# task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1 - task knowledge

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=88 -->

1. #400/task337 merged runtime remediation evidence at
   `2026-06-04T11:11:08Z`, merge commit
   `f083c9566a9f0775c27ae49f16b8b898edfc8d11`, from head
   `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.
2. The approved runtime target is
   `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`.
3. The required target model remains
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
4. The accepted all-SFT packed root remains task333:
   `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`.
5. This task is no-training preflight only. A PASS can only enable a later
   lead-gated bounded training task; it does not release task310 by itself.
6. Residuals to classify explicitly: no model construction/weight-load proof
   from task337, `nvidia-resiliency-ext` missing, and diagnostic
   `multi_storage_client` import name failure while `multi-storage-client`
   provides package path `multistorageclient`.
7. Worker_2 acceptance branch is visible at
   `d07f348eb2efef359e3aaf9fa0c2f725b57bac00`; no PR or formal mailbox
   acceptance yet.
