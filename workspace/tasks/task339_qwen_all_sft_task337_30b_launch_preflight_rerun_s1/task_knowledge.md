# task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1 - task knowledge

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

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
7. Acceptance branch base is current main
   `f083c9566a9f0775c27ae49f16b8b898edfc8d11`; lead docs were imported from
   `55d5b95cddea659f37817ebe0b161045422d40b5`.
