# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task017_m1_swe2_sandbox_runtime -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task017_m1_swe2_sandbox_runtime |
| PR | pending push |
| Session | 27 |

正在做：task017 Session 1 — SIF image mapping registry + SWE2 bridge
skeleton。新模块 `src/nemotron/recipes/super3/milestones/m1_swe2/`：
`swe2_sif_registry.yaml` 声明 3 个 SIF family (swebench/swegym/r2egym) +
filename_template；`resolve_sif_path` / `validate_sif_exists` + 严格
`instance_id` 路径注入防护（`^[A-Za-z0-9_\-]+$`）。`swe2_env_registry.yaml`
单 NeMo-Gym agent `swe_agents` 三行（一 per SIF family），今天全
m0_missing。`prepare_m1_swe2_jsonl.py` 是第三份 registry-driven bridge
copy；`coverage_report` 加 SWE2-specific `sif_source_breakdown`，运维一
眼看出哪个 container family 还差 M0 源。今天 active=0 → coverage-aware
error。19 个新 pytest case，sandbox 测试基线 88 → 107 passed。Session 2
(OpenHands wrapper + SWE-Gym trace converter) / 3 (cluster smoke) / 4
(`_bridge_base.py` 抽取) 不在本 PR。
