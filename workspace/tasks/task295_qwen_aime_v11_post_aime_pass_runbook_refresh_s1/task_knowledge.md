# task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1 - task knowledge

<!-- METADATA:SESSION=2 -->

1. Prefer refreshing existing #351 for task295 when #351 is clean/scoped; use a
   new task295 PR only if #351 cannot be safely updated.
2. #351 was refreshed in place at Session 1 because it was OPEN/base main and
   MERGEABLE before edits.
3. Current post-AIME evidence: #354/task291 merged route pass, #355/task292
   merged independent route review, #357/task294 merged independent AIME gate
   review, and #356/task293 merged corrected AIME eval-metric pass.
4. task293 metric: task285 iter2 FT `12/30 = 0.4`; accepted base remains
   `11/30 = 0.36666666666666664`; delta `+1/30`.
5. task293 local output root:
   `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`.
6. task293 remote output root:
   `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`.
7. Task293 pass is an eval-metric record only. It does not authorize export,
   endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
   30B, or 8-GPU.
8. AIME2025 prompts/labels were held out for eval/decontamination evidence only
   and are not trainable data.
9. task255 remains discarded and must not be reused.
10. #357/task294 decision is `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`; it accepts
    task293 `sampling_exact_parameter_match=false` as a bounded residual for
    metric-gate evidence only.
