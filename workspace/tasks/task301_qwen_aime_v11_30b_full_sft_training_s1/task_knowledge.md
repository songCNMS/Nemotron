# task301_qwen_aime_v11_30b_full_sft_training_s1 - task knowledge

<!-- METADATA:SESSION=15 -->

## Knowledge Entries

1. launch-gate: 30B training must not start until runtime/resource, data/packing,
   and 30B base-score gates are available.
2. output: The checkpoint handoff must be sufficient for task300 canary and
   same-harness corrected AIME2025 testing.
3. boundary: Training success is not promotion and does not authorize endpoint
   or 30B release.
4. Session 1 gate state: task298, task299, and task300 have no visible branch,
   PR, or merged task dir, so task301 must remain fail-closed before launch.
5. Never start task301 30B SFT until task298 PASS, task299 PASS, and task300
   30B base-score artifact are all recorded with exact heads/artifact paths.
6. PR #362 is the task301 acceptance/blocker report PR. Current disposition is
   `BLOCKED_UPSTREAM_GATES_MISSING`; this is expected until upstream gates are
   visible and lead clears the sequence.
7. Session 3 branch visibility: task298 is visible at
   `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`, task299 is visible at
   `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`, and task300 is visible at
   `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`; their docs are still
   `InProgress` and do not satisfy the task301 launch gates.
8. Session 4 hash clarification: the current task report content and worker
   output copy both hash to
   `8afc1629b7a42d0fa5db1a19c17f0c4dae888f88d6753c498114ec2be7e3a34c`;
   lead-observed `5924d937...` is prior PR evidence and must be reported
   separately from the refreshed output-copy hash.
9. Session 5 reconciliation: exact PR head `82cb4067e3dad6d2f8da8d94c3251e46263ff3db`
   is the report refresh that changed the report hash from
   `5924d937642a9f684c317a36c43699faaedef2f2004c94e2fd2e9830a5f60fb9` to
   `8afc1629b7a42d0fa5db1a19c17f0c4dae888f88d6753c498114ec2be7e3a34c`;
   subsequent task-local bookkeeping did not change the report content hash.
10. Session 6 lead gate: task298 runtime route is lead-approved with residuals,
    but task301 launch remains blocked until task299 final 30B data/decontam
    PASS, task300 same-harness 30B base AIME score artifact, and explicit lead
    sequence clearance are available.
11. Session 7 lead gate: task299/#365 is lead-approved with residuals at head
    `b8b760fb8f46cda8f302adbea106f19cc234e038`, but task301 launch remains
    blocked until #365 is merged/closed out, task300 provides an accepted
    same-harness 30B base AIME score artifact, and lead gives explicit launch
    clearance.
12. Session 8 lead gate: task299/#365 is merged into `main` at
    `205fc919a643b1478964a9e91793247c5e821a38`, so runtime and data gates are
    carried. Task301 launch remains blocked until task300 provides an accepted
    same-harness 30B base AIME score artifact and lead gives explicit launch
    clearance.
13. Session 9 exact-head refresh: #362 head
    `efc9aef71c97e53e71eccb3f26416cd479adf1f2` was stale because it still
    recorded #365 open/pending. Refresh #362 to carry #365 merged at
    `205fc919a643b1478964a9e91793247c5e821a38` while keeping task301 HOLD on
    task300 accepted base artifact plus explicit lead launch clearance.
14. Session 10 lead gate: task300/#363 has base-score evidence at head
    `155eb0c6845c0bf2b7d40051a9045533ffe00589` reporting 30B base `15/30`,
    but it is not accepted until worker_4 independent review and lead gate.
    Task301 launch remains HOLD until accepted base comparator and explicit
    launch clearance are available.
15. Session 11 lead gate: task300/#363 base comparator is lead-approved with
    residuals at exact head `155eb0c6845c0bf2b7d40051a9045533ffe00589`,
    reporting `15/30 = 0.5`, pending worker_3 exact-head self-merge/closeout.
    Task301 launch remains HOLD until #363 is merged/closed out and lead gives
    explicit launch clearance.
16. Prepared launch binding: task299 packed root is
    `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
17. Session 12 launch binding: lead accepted the task-owned dereferenced packed
    mirror
    `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/input/task299_packed_qwen_30b_deref_mirror`
    for launch when source/remote dereference manifests both hash to
    `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` and
    the mirror has `0` symlinks.
18. Session 12 training state: the bounded 8x H200 Qwen3-30B-A3B V11 SFT
    reached iteration `35/35`, saved checkpoint `iter_0000035`, and
    `latest_checkpointed_iteration.txt` reports `35`; skipped and NaN
    iteration counts remained `0` through iteration 35.
19. Session 14 validation watch rule: classify current live state as
    `STILL_RUNNING_VALIDATION_WATCH` while ranks remain alive, CPU activity is
    visible, GPU memory remains allocated, and the run is before the safe wait
    threshold `2026-06-02T16:53:43Z`.
20. Session 14 blocker rule: if no log progress or `train_rc.txt` /
    `train_end.txt` appears by `2026-06-02T16:53:43Z`, report
    `VALIDATION_TEARDOWN_BLOCKER_NO_LOG_PROGRESS` / `BLOCKED_VALIDATION_HANG`
    and wait for lead clearance before termination, salvage, restart, eval,
    export, endpoint, promotion, or follow-on work.
21. Session 15 salvage clearance: lead authorized graceful termination only
    after final read-only snapshot confirmed no RC/end, no validation progress,
    `latest_checkpointed_iteration.txt=35`, and `iter_0000035` present.
22. Session 15 termination result: SIGTERM to torchrun parent PID `1258209`
    produced wrapper `train_rc.txt=1` and
    `train_end.txt=2026-06-02T16:58:51Z`; torchrun propagated SIGTERM to ranks
    `1258278` through `1258285`; no SIGKILL or artifact deletion was used.
23. Session 15 final disposition:
    `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`.
    This is not a training PASS and does not clear eval/export/endpoint or
    promotion.
24. Session 15 checkpoint evidence: `iter_0000035` is `399G` with `28` files;
    inventory manifest sha256 is
    `7c7e60b5bf9a5e747e3115e37701da00b6643cd1c895e3336bef175dc6d13261`;
    checksum manifest sha256 is
    `c3f2d4b4b5d1c26041d96e5eb8799cf591acef346f75ebfdcdce40a12ec09c03`.
