# task311_qwen_all_sft_benchmark_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=7 -->

## Knowledge Entries

1. A corrected same-harness base result must exist before judging any all-SFT FT
   checkpoint on AIME2025, HMMT, MMLU-Pro, or M1 launcher-available benchmarks.
2. Non-AIME canary/checkpoint-load is required before benchmark evaluation.
3. Eval-only export or endpoint may be used only if required for evaluation and
   must not be described as promotion.
4. Task311 branch was accepted from `origin/main`
   `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`; merged task310 docs on that
   base contain task creation only, so any canary/benchmark action depends on a
   later verified task310 checkpoint handoff.
5. Lead follow-up confirmed task311 remains blocked on task310 checkpoint
   handoff and must perform checkpoint-load/non-AIME canary before benchmark
   eval once that handoff exists.
6. Session 2 blocker artifact is
   `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T143618Z/manifests/blocker_manifest.json`
   with sha256
   `7b90155bc4f31bea4ccb5a67472d0c5d703c5607b0ec0a20d0523bdadc179ed8`.
7. PR #371 records the task311 blocker/status docs for lead review.
8. Lead verified PR #371 at head
   `37a76caea59a2ca27c5d4cbc5d2e98d46d100420` and kept task311 on HOLD pending
   task312 independent review plus upstream task309/task310 refresh; canary and
   benchmarks remain prohibited until an accepted task310 checkpoint handoff
   exists.
9. Lead later confirmed task311/#371 remains HOLD at head
   `6981a654c1c72c72dfb57fd42aa60cc15b0a9f77`; task309/#372 refreshed
   constrained PASS, but task310 still has no accepted checkpoint handoff and
   no task311 canary/benchmark action is authorized.
10. Lead gate update for Session 5 reiterates the required future order:
    refresh task311 from current main after accepted task310 checkpoint handoff,
    run checkpoint-load/non-AIME canary first, then run corrected same-harness
    benchmark eval only if that canary passes.
11. Lead confirmed prerequisites #374/#372/#375 are merged and task310 is
    released to worker_5, but task311 remains HOLD until an official task310
    checkpoint handoff is accepted; stale #371 must not be self-merged or used
    to run canary/benchmarks.
12. Task310 produced only a salvage checkpoint candidate at PR #373 head
    `7561a578` with `train_rc=1` after validation hang; task313 review is now
    required before lead may release task311 checkpoint-load plus non-AIME
    canary.
