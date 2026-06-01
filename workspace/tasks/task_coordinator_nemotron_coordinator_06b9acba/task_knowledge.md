# task_coordinator_nemotron_coordinator_06b9acba - Task Knowledge

<!-- METADATA:SESSION=18 -->

## Knowledge Entries

1. 本任务是 coordinator 生命周期任务，只要 coordinator 存在就不可完成。
2. Coordinator 恢复中断工作时只做审计、目标设置和跟进；普通代码实现、测试和 merge 必须经由 `intern_nemotron_lead` 分配给 worker。
3. 当前 Nemotron workspace 可能包含大量旧 assignee 名称的历史 InProgress/Working task；恢复时需要 lead 先确认真实未完成工作，再映射到当前 `intern_nemotron_worker_*`。
4. 恢复中断任务时，优先级应以“未合入 origin/main 的旧分支/PR 证据”为准，而不是单纯依赖 workspace/tasks 中的旧状态标签。
5. 本轮恢复采用 primary+independent audit 配对：task231 由 worker_1 主审、worker_4 独立核验；task217 由 worker_2 主审、worker_5 独立核验；task203/206/209 由 worker_3 形成 coverage matrix 后再决定是否需要恢复。
6. Lead-authored coordination PRs such as #313 require non-author or otherwise authorized approval/merge; worker closeout PRs depending on a lead PR should land only after the lead PR lands, and stacked PRs like #316 must be retargeted/rebased before final merge.
7. When a gate update reports no approval/merge change, the coordinator should keep the existing hold state and only ask for immediate updates on approval, merge, base, or mergeability changes.
8. Pure lead-bookkeeping head-only updates to #313 do not require immediate coordinator escalation when #313 remains open/clean/unapproved/unmerged and worker PR base/mergeability/head state is unchanged.
9. If `codeup_pr merge` fails with token permission 403 but GitHub CLI is authenticated and the user authorized merge, `gh pr merge --squash` can merge the intended PR; retain a merged PR's branch when another PR is still stacked on it.
10. After a lead PR lands, worker PR GitHub state can change before mailbox reports arrive; coordinator should recheck PR heads/mergeability and route follow-up through lead rather than contacting workers directly. Even if PRs become mergeable, lead gate approval and worker self-merge sequencing still apply.
11. Recovery closeout completed with #313/#314/#315/#316 merged: no new implementation tasks were created; final dispositions are task203/task206/task209 covered/no recovery, task231/task228 blocked/HOLD, and task217 approve close with one-iteration smoke residual risk.
12. Lead-side archive was confirmed at commit `04582ca`; permanent coordinator and lead lifecycle tasks remain Working/InProgress after recovery closeout.
13. Project resource constraints for the AIME 2025 Qwen effort: debug/training on `NemTron`, sync code to `/root`, use `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` for cheaper pilots, download locally before copying to `NemTron`, and never delete existing files under `/mnt/cephfs/data/processing/lei.song`.
14. Current Qwen hard-math state to reuse: task071/task075/task076 contain the relevant pipeline history; PR #178 and PR #183 are merged; V7 passed corrected AIME25 at `0.21`, V8 failed AIME25 at `0.1966666667`, and corrected V9 still failed targeted `aime_06` despite parsed `10/10`.
15. AIME 2025 Qwen promotion gate: establish a same-harness base Qwen score first, do not train on AIME 2025 labels/prompts except held-out eval/decontamination, use a Qwen3-4B pilot before any full 30B/8-GPU scale, and promote only if fine-tuning does not lower AIME 2025 versus base under the same corrected protocol.
16. If `/api/intern/goal/set` returns `unconfirmed` for long multi-line content, write the detailed handoff into a task note and retry with a concise one-line goal pointing to that file.
17. Lead split the AIME 2025 Qwen work into task241 data sidecar, task242 planner/smoke scripts, task243 base-vs-FT eval gate, task244 independent contamination/regression review, and task245 artifact/runbook verification; coordinator should track all five as one gated workstream.
18. For the V10 Qwen AIME workstream, the first measurable go/no-go is task243's same-harness Qwen3-4B base score versus task241/task242's V10 FT smoke score, with exact-normalized accuracy plus parsed/finish diagnostics.
19. Qwen AIME live-gate state as of lead Session 47: #325/task246 corpus evidence and #326/task247 Qwen3-4B base smoke are merged; accepted same-harness base score is `11/30 = 0.36666666666666664`; first V10 gate remains `NO-GO/HOLD` until task248 FT artifacts and task243 same-harness base-vs-FT comparison exist.
20. If an approved worker PR head advances before merge, recheck the delta and require fresh lead/worker handling for any material change; status/history/task_knowledge-only drift with unchanged review matrix can remain sequenced, but merge still requires clean state at merge time.
21. Current sequencing for #324/#323: worker_5 #324 runbook self-merge first if clean; worker_4 #323 contamination review only after #324 merges and #323 remains clean, with docs/status refresh and report required if #324 makes #323 dirty or stale.
