# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task015_m1_rlvr_full_mix -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task015_m1_rlvr_full_mix |
| PR | pending push |
| Session | 23 |

正在做：task015 Session 1 — registry-driven RLVR mix derivation。新文件
`src/nemotron/recipes/super3/milestones/m1_rlvr/rlvr_env_registry.yaml`
全量声明 21 NeMo-Gym envs（一行 mix + m0_env_id + status + 元信息）。
`prepare_m1_rlvr_jsonl.py::MIX_PROFILES` 改成 import-time 从 registry 派
生；future task057 把 m0_missing 翻成 active，bridge 自动 pickup，不需要
改 Python。Manifest 加 `coverage` 块。**关键 correction**：task014 Session 1
的 `RLVR1_ENV_MAP` 用了两个 NeMo-Gym 找不到的名字 (`general_tool_calling`
/ `search_grounded_qa`)；本 Session rename 第一个为
`single_step_tool_use_with_argument_comparison` (verifier 语义匹配)、把
第二个登记成 `m0_missing` 让 coverage 看得见 gap。新 9 个 pytest case，
sandbox 测试基线推到 75 passed。Session 2+ 等 task057 / task056 Session 2
/ task016 把 m0_missing 翻成 active，bridge 自动 pickup。
