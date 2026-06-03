# task326_qwen_all_sft_next_phase_safety_review_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Task322-task325 are prerequisites, not runtime release.
2. Later training/eval requires accepted evidence from raw materialization,
   validation-skip preflight, blend design, and M1 route/blocker tasks.
3. This task does not authorize runtime action or merge.
4. Current task322/#388 head
   `adf1a02f3cd5da11d04d2a4d167bdb8d1573e79f` has lead gate
   `APPROVE_PARTIAL_EVIDENCE_WITH_EXCLUSIONS / HOLD_FULL_ALL_SFT_PACK_TRAIN`.
   Two sources are included/materialized with 23,997 rows and 0/0/0 decontam
   hits; 10 large sources remain fail-closed `EXCLUDED_SIZE_GT_1GB` blockers.
5. Current task323/#385 head
   `de480248b1ad7abe16a620729e62fa397443228d` has lead current-head
   carry-forward `APPROVE_ROUTE_A_PREFLIGHT_DOCS / HOLD_TRAINING`. It is not
   optimizer/training/eval/export/endpoint/promotion clearance.
6. Current task324/#386 head
   `8c4f7aa72f07e69e400789fced12acb17cf80cb7` has lead gate
   `APPROVE_BLEND_DESIGN_DOCS / NO_ACTION_RELEASE`. Treat as design docs only.
7. Current task325/#387 head
   `e07ee3f9268b33658e18881c25a3d221bf2136ee` has lead gate
   `APPROVE_BLOCKER_DOCS / BLOCK_RUNTIME_CONFIRMED`. M1 runnable rows remain
   `0/19`.
8. task319/#383 is accepted only as feasibility docs/no pack-train release;
   task322 must provide exact materialized rows/checksums/decontam/split proof
   before any packed contract.
9. task318/#384 is accepted only as preflight planning/HOLD training; task323
   must be lead-gated and any later launch task must re-prove train-only valid
   exposure `0`, `do_validation=false`, and same-harness eval handoff before
   optimizer launch.
10. task320/#381 requires future repair to preserve math gains while fixing
   non-math MMLU-Pro retention; task324 must express bucket/source constraints
   before any packed blend handoff.
11. task315/task325 keep M1 rows held until a launcher runtime route is proven
    or `BLOCK_RUNTIME_CONFIRMED` is fully documented.
12. Worker PR for task326 is #389.
13. Full all-SFT packed/training handoff remains blocked until the 10 excluded
    task322 large files plus supervised-token counts, split exposure parity,
    Qwen chat-template packing proof, and full decontam contract are accepted
    in a later resource-approved task.
