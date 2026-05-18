# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 24 |

最近：task015 Session 1 (PR #36 `f4ed9ae`) 已 squash-merge 进 main —
新增 `src/nemotron/recipes/super3/milestones/m1_rlvr/rlvr_env_registry.yaml`
全量声明 21 NeMo-Gym envs，`prepare_m1_rlvr_jsonl.py::MIX_PROFILES` 改
registry-driven import-time 派生，manifest 加 coverage 块。**关键 bug fix**：
task014 Session 1 的 `RLVR1_ENV_MAP` 用了两个 NeMo-Gym 找不到的名字
(`general_tool_calling` / `search_grounded_qa`)，本 PR rename + 移除并登
记成 `m0_missing`，避免 task014 Session 2 cluster verify 时 router 失败。
9 个新 pytest case (9 → 18 task015 总数；sandbox 总数 66 → 75 passed)。
task015 整 task 仍 InProgress：Session 2+ 等 task057 / task056 Session 2 /
task016 把 m0_missing / verifier_mismatch / blocked_external 行翻成 active，
bridge auto-pickup。
