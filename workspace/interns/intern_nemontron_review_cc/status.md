# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 16 |

最近：task012 (PR #28 `04681a7`) — REVIEW_v0.md #8 chat template (从 v1 起 still-open) 终于落地。Super3 ship 独立 `super3.jinja` (verbatim copy of nano3 + lineage header)；resolver `_BUILTIN_TEMPLATES` 同时认 nano3/super3；三个 data-prep yaml flip 到 `chat_template: super3`；roundtrip smoke 常量 rename；新加 4 个 render-time 测试 (sandbox 测得 3 passed + 1 skipped pydantic-gated)。REVIEW_v0.md 18 fixed / 1 partial / 1 still-open (#9 two-stage SFT loss, queued as task013) / 2 tracked。
