# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 22 |

最近：task014 Session 1 (PR #34 `4a50941`) 已 squash-merge 进 main —
新增 `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py`
(M0 → RLVR1 JSONL bridge + NeMo-Gym env map + lineage 接 M0 manifest)，
`RLVR1_ENV_MAP` 4 个映射严格按 roadmap §1.3 (math_with_judge / code_gen /
search_grounded_qa / general_tool_calling)，9 个新 pytest case。task014
整 task 仍 InProgress：Session 2 (RLVR1 config wiring + smoke launcher)
要 NemTron cluster 验证，待开。Sandbox 测试基线推到 66 passed + 1 skipped。
