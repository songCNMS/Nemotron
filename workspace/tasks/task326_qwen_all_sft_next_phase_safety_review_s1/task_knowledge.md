# task326_qwen_all_sft_next_phase_safety_review_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Task322-task325 are prerequisites, not runtime release.
2. Later training/eval requires accepted evidence from raw materialization,
   validation-skip preflight, blend design, and M1 route/blocker tasks.
3. This task does not authorize runtime action or merge.
4. At review time task323/#385 was visible at head
   `edb265351b9f369698f561527cd27f2978f649ba` with worker-reported
   `PASS_ROUTE_A_PREFLIGHT`, but no lead gate comment. Treat it as pending
   lead review, not training clearance.
5. At review time task324/#386 was visible at head
   `8c4f7aa72f07e69e400789fced12acb17cf80cb7` with worker-reported
   `APPROVE_BLEND_DESIGN`, but no lead gate comment. Treat it as pending lead
   review and still blocked on task322 before any packed contract.
6. At review time task325/#387 was visible at head
   `e07ee3f9268b33658e18881c25a3d221bf2136ee` with worker-reported
   `BLOCK_RUNTIME_CONFIRMED`, but no lead gate comment. Treat M1 eval rows as
   held. Drift from first report head `e6c5e1f` is metadata-only.
7. At review time task322 had no visible branch or PR and remains pending
   substantive evidence.
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
