# task311_qwen_all_sft_benchmark_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

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
