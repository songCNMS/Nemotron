# task311_qwen_all_sft_benchmark_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. A corrected same-harness base result must exist before judging any all-SFT FT
   checkpoint on AIME2025, HMMT, MMLU-Pro, or M1 launcher-available benchmarks.
2. Non-AIME canary/checkpoint-load is required before benchmark evaluation.
3. Eval-only export or endpoint may be used only if required for evaluation and
   must not be described as promotion.
4. Session 78 task310 produced only a salvage checkpoint candidate; task311 must
   wait for accepted task313 review and explicit lead release before
   checkpoint-load or non-AIME canary.
5. After task313/#376 merged at `cb36dcab` and task310/#373 merged at
   `292c5bfa`, lead released only checkpoint-load plus non-AIME
   canary/completion-retention for checkpoint
   `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`.
6. Benchmark eval, AIME/task243 eval, MMLU-Pro/HMMT/M1 basket eval, export,
   endpoint, promotion, additional training, task255 reuse, AIME2025 train data,
   shared deletion, self-merge, and main push remain HOLD until canary evidence
   is reported and lead releases the next gate.
7. Worker_3 official canary mailbox `f4666ec4` and #371 head `2ffbe8c4`
   establish `PASS_NON_AIME_CANARY_ONLY`: checkpoint load passed, remote rc `0`,
   5/5 completions retained, 5/5 exact expected-answer matches, and no
   empty/mixed-script/degeneration failures.
8. Lead released corrected benchmark evaluation only after accepting the canary:
   MMLU-Pro, AIME2025, HMMT, and runnable M1 launcher-available basket rows.
9. Same-harness base evidence is mandatory before judging FT for each benchmark;
   prior base can be reused only when model path, route, evaluator, prompt
   protocol, sampling, parser, and denominator match exactly.
10. Post-release recheck found no official worker_3 benchmark report and no
    #371 head drift beyond `2ffbe8c4`; pane-only benchmark exploration is not
    gate evidence. Lead follow-up was delivered requiring official metrics or
    blockers with commands/env, artifact roots, checksums, completions, parser
    diagnostics, and same-harness base proof.
11. Worker_3 later had an unofficial uncommitted Session 9 route-gate draft:
    corrected Qwen endpoint runners need eval-only HF export/endpoint for
    task310, while direct no-export judgment needs task298 base Megatron reruns
    before FT comparison. The draft is not lead-accepted until #371 is
    refreshed and a mailbox report is processed.
12. Lead accepted the route-gate report at #371 head `34ffa587` as route
    analysis only, with route report sha
    `4d3e7da79da922167a7d8f5bacc990ed9201ee8cd2953fcf57c07b9cdae52412`.
13. Worker_3 official mailbox `7f3481c90ee447cc80f3fe3a9516f995` confirmed
    no benchmark/export/endpoint/training at the accepted route-gate head and
    was marked read by lead.
14. Current #371 head `1ce85c63` is bookkeeping-only drift from `34ffa587`;
    route report sha is unchanged and #371 is OPEN/CLEAN.
15. Lead released only eval-only export/endpoint preflight plus same-harness
    benchmark execution at current head `1ce85c63`. Same-harness base evidence
    is mandatory before judging FT; fail closed on export/endpoint/input/
    launcher/base blockers.
