# nemotron_lead - Task Knowledge

<!-- METADATA:SESSION=19 -->

## Knowledge Entries

1. 本任务是 team lead 生命周期任务，只要 team 存在就不可完成。
2. `internctl team assign-worker-task` writes to `/work-agents/<project>` and pushes the default branch, so this lead session used manual task docs on a worker branch to respect the no-direct-main-push rule.
3. Deleted/stale assignees `intern_nem_dev_*` and `intern_nemontron_*` must be mapped to current `intern_nemotron_worker_*` owners before recovery continues.
4. When worker PRs are built from lead-created task docs, land the initial task-doc PR first or retarget/rebase stacked worker PRs; #316 was stacked on #313 while #314/#315 target `main`.
5. #313 is the gate for worker closeout sequencing: until it receives non-author approval/merge, do not direct workers to finalize #314/#315; #316 remains stacked and must be retargeted/rebased to `main` or explicitly sequenced after #313 before final merge.
6. Bookkeeping-only #313 head movement does not require immediate coordinator escalation when #313 remains open/clean with blank `reviewDecision`/no merge and #314/#315/#316 base, mergeability, and head are unchanged; record it locally and continue monitoring.
7. A user-side "merge the pr" request should be treated as authorization intent, not as permission for `intern_nemotron_lead` to self-merge; route the request to the coordinator or another authorized non-author merge owner while preserving the #313 -> #314/#315 and #316 retarget/rebase sequencing.
8. After a lead task-doc PR lands, downstream docs/status PRs can become `DIRTY` because they touch the same workspace closeout files; the owning workers must refresh their branches against `main`, preserve the gate disposition unless new evidence appears, and report new head/base/mergeability before any final merge direction.
9. Lead approval for downstream closeout PRs requires worker mailbox evidence plus independent GitHub state and file-list checks; after approval, instruct the worker to self-merge if still mergeable, and do not run `gh pr merge` from the lead seat.
10. If an approved downstream PR head advances before merge, request a new worker mailbox report for that head; if the merge completes before the report arrives, record the final head, merge commit, mergedBy, and later reconcile the worker's final-head report when it lands.
11. Coordinator-confirmed recovery closeout should be archived in lead history/status, but `nemotron_lead` stays Working/InProgress because it is the permanent team lead lifecycle task.
12. In monitoring state with no mailbox items, residual cleanup, new user request, or abnormal regression, do not create worker tasks or send extra coordinator updates beyond required session bookkeeping.
13. Qwen AIME25 improvement work has a hard non-regression rule: no fine-tuned Qwen checkpoint can be promoted unless it is scored against the same base Qwen checkpoint under the same corrected AIME 2025 evaluator/protocol and the FT score is not lower.
14. For this Qwen AIME25 priority, run Qwen3-4B pilot/debug first using `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`; do not spend 30B/8-GPU scale until the 4B pilot is non-regressing or produces a concrete evaluator/data fix.
15. AIME 2025 prompts and labels are held-out eval/decontamination material only; worker tasks must not add them to training data, sidecars, distillation prompts, or answer-supervision rows.
16. For the Qwen AIME25 split, remote branch presence alone is not gate evidence: worker mailbox reports and PR artifacts are still required before lead can approve data/planner/eval/review/runbook work or authorize pilot execution.
17. For task243, a baseline protocol that points at `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507` does not satisfy the supervisor's Qwen3-4B pilot requirement; the accepted debug checkpoint path is `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
18. A worker-reported missing model path is not a true resource blocker if it used the wrong Qwen3-4B path; require path correction before escalating base-score resource availability.
19. When task245/runbook verification cites upstream task or PR state, it must be refreshed after those upstream PRs move; a stale blocker such as the old task243 `/mnt/3fs` path or pre-#320 task241 no-PR state is request-changes even if the overall NO-GO conclusion remains true.
20. For #320/task241, worker-reported tests are useful gate input but lead should not rerun them; require independent review of AIME25 heldout/decontam handling before approval because the hard rule forbids trainable AIME25 prompt/label leakage.
21. For #321/task242, planner/smoke PR evidence removes the old "no task242 PR" blocker, but it does not satisfy first go/no-go by itself; real held-out decontam/AIME input, endpoint, base-score artifacts, FT checkpoint/export/eval, and worker_4/worker_5 refreshed reviews are still required.
22. If #317/task245 runbook still lists "task242 has no published PR" after #321 exists, keep #317 in request-changes/HOLD even though the global NO-GO conclusion is still correct.
