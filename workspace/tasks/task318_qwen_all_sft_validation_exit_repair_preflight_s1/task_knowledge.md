# task318_qwen_all_sft_validation_exit_repair_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=95 -->

## Knowledge Entries

1. Task310 train loop reached iter 35/35, but validation hung and `train_rc=1`.
2. Task313 approved task310 checkpoint only for load/canary handoff, not clean
   training success.
3. A future 30B run must have explicit validation/exit/rc/checkpoint teardown
   behavior before optimizer launch.
4. This task does not authorize training or eval.
5. Task318 preflight found that `train.py` sets `do_validation=True` when
   `${super3_packed_sft_dir}/valid/*.parquet` exists and sets
   `do_validation=False` only when no valid parquet is exposed.
6. Task310 preflight recorded `do_validation=true` and
   `packed_val_data_path=.../valid_4096_valid.npy`; the training log then hung
   at `Evaluating on 80 samples` / `Evaluating iter 1/10`.
7. The Qwen 30B entrypoint exposes `train.eval_interval` but no reviewed
   explicit validation disable or validation timeout knob.
8. Recommended next gate is a later implementation/launch task that either
   proves an explicit train-only root with same-harness eval handoff or proves
   bounded built-in validation with no-progress timeout, rc, checkpoint, and
   teardown policy.
9. Worker status values must use allowed states. As of Session 94, developer
   context says worker_5 is Idle with no active task; #384 remains an open
   provenance PR and does not require keeping worker status `Working`.
10. Lead gate for task318/#384 accepted head `2cdf39fd` as
    `APPROVE_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED / HOLD_TRAINING`;
    this does not authorize implementation, training, self-merge, or any
    runtime/eval/export/promotion action.
11. Task323 is the lead-assigned Route A follow-up for validation-skip
    preflight; task318 remains a planning-evidence PR and must not be
    self-merged by worker_5.
12. Task323 #385 is merged at `2026-06-04T13:13:07Z`, merge
    `8a757c323b82f4330b765ee89a6d78f421d9d9be`; it provides the concrete Route
    A preflight proof that task318 required as a later task.
13. Task311 #371 and task314 #380 are merged on current main, while task341
    #404 and task342 #405 keep training-readiness/NemTron access blocked.
14. Session 94 refreshed #384 from `origin/main`
    `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`; the prior DIRTY state was a
    status-only conflict, and the refreshed PR remains docs-only with no
    implementation, task310/task341 release, or runtime action.
15. #377/task316 merged at `2026-06-04T13:57:09Z`, merge commit
    `928d9d684b188fc1858914d0de7aef211627f697`, merged head
    `19f8a01f44aa4322635aab374d8ed22795639bda`.
16. Session 95 refreshed #384 from the new `origin/main`
    `928d9d684b188fc1858914d0de7aef211627f697`; #384 remains
    validation-exit provenance only and may be closed as superseded by merged
    #385 Route A proof if lead chooses.
