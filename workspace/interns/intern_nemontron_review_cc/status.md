# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 48 |

最近：task030 Session 4 (PR #61 `159d81f`) 已 squash-merge 进 main —
bridge / M0 module-local loader merge into schema layer。重审 Session 1
/ Session 2 closeout 反复强调的"两层不要合并"决策后找到正确合并粒度：
**合并 row-shape definitions (single source of truth)，不合并
aggregation behavior (fail_fast runtime vs collect-all audit)**。
`schema.validate_rows` 加 `fail_fast=False` + `source_path` 参数；
`validate_top_level` 加 `strict=True`。4 个 runtime loader refactor 成
thin wrapper 委派到 schema，module-specific 检查包成 `extra_validators`
closure。零外部行为变化，226 原测试不动，新加 7 个 schema API surface
test。Sandbox 测试基线 226 → 233 passed + 6 skipped。

task030 整 task 仍 InProgress：Session 3 (M1 eval basket — block on
task019/020) 待开。

下一个候选 (sandbox-runnable):
- **task058 follow-ups** — license/contamination 额外校验加进 schema 层
  (e.g., share-alike cascade 检测，CC-BY-SA 数据流到哪些 derived artifact)
- **task019 / task020** — M1 eval basket (本身 sandbox-runnable；acceptance
  要真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都需 cluster / Docker / nvcr container
