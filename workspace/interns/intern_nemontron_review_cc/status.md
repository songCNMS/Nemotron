# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task012_super3_chat_template -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task012_super3_chat_template |
| PR | pending push |
| Session | 15 |

最近：开 task012 — REVIEW_v0.md #8 chat template (从 v1 起 still-open) 终于落地。Super3 ship 独立 `super3.jinja` (verbatim copy of nano3 + lineage header)；`_apply_chat_template` 通过 `_BUILTIN_TEMPLATES = {"nano3", "super3"}` 同时解析；三个 data-prep yaml flip 到 `chat_template: super3`；roundtrip smoke 常量 rename；新加 4 个 render-time 测试。
