# nemotron_lead - Task Knowledge

<!-- METADATA:SESSION=13 -->

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
