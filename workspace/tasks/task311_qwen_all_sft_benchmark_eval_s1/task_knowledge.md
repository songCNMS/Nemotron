# task311_qwen_all_sft_benchmark_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=10 -->

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
13. After task313/#376 and task310/#373 merged, lead released only
    checkpoint-load plus synthetic non-AIME canary/completion-retention for
    task310 checkpoint
    `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`;
    benchmark eval, AIME/task243 eval, MMLU-Pro/HMMT/M1 basket eval, export,
    endpoint, promotion, additional training, task255 reuse, AIME2025 train
    data, shared deletion, self-merge, and main push remained held.
14. Task311 canary run `run_20260603T173607Z` used local artifact root
    `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`
    and remote artifact root
    `/root/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`.
15. The no-export/no-endpoint route was
    `direct_in_process_mcore_static_engine_no_export_no_endpoint_30b_tp4_pp2_ep4_etp1_topk1_greedy`
    with 8 H200s, TP=4, PP=2, EP=4, ETP=1, source head
    `d2e275e3ec775cd8f73f7bdeeb0bd7f07b44c372`.
16. Checkpoint-load proof rank0 for task310 iter 35 passed:
    `load_megatron_model=PASS`, model `Float16Module`, unwrapped `GPTModel`,
    dtype `torch.bfloat16`, eval true, hidden size 2048, 48 layers, 32
    attention heads, sequence length 4096, padded vocab size 151936.
17. Canary disposition is `PASS_NON_AIME_CANARY_ONLY`: 5 prompts requested,
    5 completions retained, 5 non-empty responses, 5 exact expected-answer
    matches, zero empty/mixed-script/degeneration counts, remote rc `0`.
18. Key canary hashes: summary
    `5da06d50f23bd581d2de5988f999cc4a2d7bb162f487afef1033c29810ce93b5`,
    decision
    `7678a8f8f3445882a1e5ea575169d37aae7f7ad9ead14b4f5d788fa5c5cb3ba5`,
    full completions
    `fd86644308d690340545be0fb308912dac87ddd8c3b499e2af4556635c3409f7`,
    prompt manifest
    `3838d39a779bd28df90ced9a1f9ba99f61bdb3dd747083450be0334cdf52c0b2`,
    checksum manifest
    `cc0f2be1d99e4b1caad4e5eb4e4e7d6f6a3bf99be2d28ff0c9e9b2beb23307d4`.
19. Benchmark reports remain `HOLD_NOT_RUN` because the authorized task311
    action stopped after checkpoint-load and non-AIME canary. No corrected Qwen
    benchmark, AIME/task243 eval, HMMT, MMLU-Pro, or M1 basket row was run.
20. Lead accepted task311 non-AIME canary at exact #371 head
    `2ffbe8c4d9f833980d64d756965e909bf3260f20`, then clarified that any
    benchmark row requiring eval-only export or endpoint must be reported as an
    eval-only route/blocker before execution.
21. Established corrected Qwen benchmark routes are endpoint-based for
    MMLU-Pro/AIME2025/HMMT through task071/task300 evidence. Task310 is a
    Megatron checkpoint, so that route requires eval-only HF export plus
    eval-only SGLang endpoint before FT endpoint metrics can be collected.
22. Accepted task300 AIME base `15/30 = 0.5` can be reused only for an endpoint
    FT run matching model family, route, evaluator, prompt variant, sampling,
    parser, normalizer, and all-request denominator. Direct no-export runs
    cannot claim exact same-harness reuse of that endpoint base.
23. Direct no-export alternative for AIME/HMMT/MMLU-Pro would need same-route
    base rerun from task298 imported Megatron checkpoint
    `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`
    and FT run from task310 `iter_0000035`, with identical evaluator, prompts,
    sampling, parser, selected-rank policy, and denominator.
24. M1 launcher mapping has 14 exact launcher-available rows and 5 exact-missing
    rows. Missing rows are `multichallenge`, `terminalbench`, `mcp_mark`,
    `tool_decathlon`, and `swe_bench_verified`; listed candidate tasks are not
    equivalent substitutes.
25. Session 10 formal route-gate report is
    `workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/all_sft_benchmark_route_gate_report.md`;
    disposition remains
    `HOLD_EVAL_ONLY_EXPORT_ENDPOINT_ROUTE_REPORT_BEFORE_RUN`.
