# nemotron_lead - Task Knowledge

<!-- METADATA:SESSION=7 -->

## Knowledge Entries

1. 本任务是 team lead 生命周期任务，只要 team 存在就不可完成。
2. `internctl team assign-worker-task` writes to `/work-agents/<project>` and pushes the default branch, so this lead session used manual task docs on a worker branch to respect the no-direct-main-push rule.
3. Deleted/stale assignees `intern_nem_dev_*` and `intern_nemontron_*` must be mapped to current `intern_nemotron_worker_*` owners before recovery continues.
4. When worker PRs are built from lead-created task docs, land the initial task-doc PR first or retarget/rebase stacked worker PRs; #316 was stacked on #313 while #314/#315 target `main`.
5. #313 is the gate for worker closeout sequencing: until it receives non-author approval/merge, do not direct workers to finalize #314/#315; #316 remains stacked and must be retargeted/rebased to `main` or explicitly sequenced after #313 before final merge.
