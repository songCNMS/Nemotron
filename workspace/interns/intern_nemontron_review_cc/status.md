# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 46 |

最近：task021 Session 6 (PR #59 `4f651f6`) 已 squash-merge 进 main —
rollout policy guard rail。新加 `ROLLOUT_POLICY_ORACLE` /
`ROLLOUT_POLICY_ADVERSARIAL` 常量 + `recommended_container_runtime`
helper。`run_python_unit_tests` 加 `rollout_policy` kwarg：adversarial +
container_runtime=None → RuntimeError；oracle (默认) → 字节级保留 Session
5 in-process 行为。决策记录：原 plan "literal default flip" 在 in-repo
无 coherent target，改 guard rail 同等安全效果。11 个新 pytest case，
sandbox 测试基线 215 → 226 passed + 6 skipped。

task021 整 task 仍 InProgress：Session 4 (NeMo-RL / Ray / vLLM cluster
verify — block on NemTron access) 待开。

下一个候选 (sandbox-runnable):
- **task058 follow-ups** — license/contamination 额外校验加进 schema 层
  (e.g., share-alike cascade 检测)
- **task030 Session 4** — Bridge / M0 module-local loader 接进 schema 层
  (careful refactor，runtime fail-fast 不能 break)
- **task019 / task020** — M1 eval basket (本身 sandbox-runnable；acceptance
  要真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都需 cluster / Docker / nvcr container
