# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 26 |

最近：task016 Session 1 (PR #38 `d04b694`) 已 squash-merge 进 main —
新模块 `src/nemotron/recipes/super3/milestones/m1_swe1/` + 镜像 task015
registry-driven 模式的 `swe1_env_registry.yaml` + `prepare_m1_swe1_jsonl.py`。
今天 SWE1 active=0，`prepare()` raise coverage-aware error；Session 2
落 M0 SWE pivot converter (SWE-Gym-Lite / R2E-Gym) 翻一行 active 之后
bridge 自动 pickup。13 个新 pytest case，sandbox 测试基线 75 → 88 passed。
task016 整 task 仍 InProgress：Session 2 (M0 converter) + Session 3
(cluster smoke launcher) 待开。下一个 critical-path 候选 (roadmap §5)：
task017 (M1 SWE2 sandbox runtime / OpenHands loop) 或 task013
(two-stage SFT loss) 或 task018 (RLHF GenRM service)。
