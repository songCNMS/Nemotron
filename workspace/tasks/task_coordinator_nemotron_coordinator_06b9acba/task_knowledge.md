# task_coordinator_nemotron_coordinator_06b9acba - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. 本任务是 coordinator 生命周期任务，只要 coordinator 存在就不可完成。
2. Coordinator 恢复中断工作时只做审计、目标设置和跟进；普通代码实现、测试和 merge 必须经由 `intern_nemotron_lead` 分配给 worker。
3. 当前 Nemotron workspace 可能包含大量旧 assignee 名称的历史 InProgress/Working task；恢复时需要 lead 先确认真实未完成工作，再映射到当前 `intern_nemotron_worker_*`。
4. 恢复中断任务时，优先级应以“未合入 origin/main 的旧分支/PR 证据”为准，而不是单纯依赖 workspace/tasks 中的旧状态标签。
5. 本轮恢复采用 primary+independent audit 配对：task231 由 worker_1 主审、worker_4 独立核验；task217 由 worker_2 主审、worker_5 独立核验；task203/206/209 由 worker_3 形成 coverage matrix 后再决定是否需要恢复。
