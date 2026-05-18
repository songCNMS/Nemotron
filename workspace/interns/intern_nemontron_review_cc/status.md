# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task016_m1_swe1_pivot_data -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task016_m1_swe1_pivot_data |
| PR | pending push |
| Session | 25 |

正在做：task016 Session 1 — SWE1 bridge skeleton。新模块
`src/nemotron/recipes/super3/milestones/m1_swe1/` + `swe1_env_registry.yaml`
（两行：m0_missing 槽 + verifier_mismatch 给现有 SWE-bench Lite 源）+
`prepare_m1_swe1_jsonl.py`。Bridge 模式镜像 task015 Session 1 的 registry-
driven 派生（80% 重复 m1_rlvr 代码；task017 SWE2 落第三版时抽 base）。
今天 active=0 → `prepare()` raise coverage-aware error；Session 2 落 M0
SWE pivot 数据 converter + registry 翻 active 之后 bridge 不需 Python 改
动。13 个新 pytest case，sandbox 测试基线推到 88 passed。Session 2 (SWE-Gym-
Lite / R2E-Gym converter) + Session 3 (cluster smoke) 不在本 PR。
