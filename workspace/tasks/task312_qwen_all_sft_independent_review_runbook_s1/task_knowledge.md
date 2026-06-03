# task312_qwen_all_sft_independent_review_runbook_s1 - Task Knowledge

<!-- METADATA:SESSION=77 -->

## Knowledge Entries

1. Independent review must check task308-task311 evidence, not only final
   summary metrics.
2. Any all-SFT closeout must preserve non-promotion wording unless a separate
   supervisor gate explicitly authorizes promotion.
3. The sampling/backend residual from task306 was acceptable only for fail
   closeout and should not be treated as sufficient for a pass/promotion claim.
4. Session 79 visible upstream state: task308 `348cba44`, task309 `d054925b`,
   and task311 `dd59d544` are acceptance-only branches without substantive
   reports/artifact roots; task310 has only task-creation docs on `origin/main`
   `172cd0e7` and no worker branch/report/artifacts. Combined task312 decision
   is `REQUEST_CHANGES_HOLD_WAITING_UPSTREAM_EVIDENCE`.
5. Until task308-task311 provide exact reports, artifact roots, commands/env,
   checksums, metrics, unavailable benchmark rows, and boundary proof, no
   all-SFT closeout, promotion, export, endpoint, benchmark comparison, further
   scale decision, or merge authorization is supportable.
6. Lead baseline clarification: use `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`
   as current main / branch base and
   `ecb14173a820df377270273b9f7d9d92cb5076d2` as unchanged product-code
   baseline for task312 provenance.
7. Session 81 refresh: #374/task308 current head `f57384f6` is approved as
   `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`; the requested #374 head
   `4a46c9b` drifted by worker_1 status/history only. #372/task309 at
   `998ebce4` needs refresh/rerun from #374. #373/task310 at `1cd3eb17` and
   #371/task311 at `37a76cae` are approved as blocker closeouts with freshness
   residuals because no current task309 packed contract or task310 checkpoint
   handoff exists.
