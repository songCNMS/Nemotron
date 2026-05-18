# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

- 由 task011 implementation roadmap 派生：本 task 是 REVIEW_v0.md #8 chat template 的落地点，跨越 v1 (2026-05-17) → v6 (2026-05-17 task008) 一直 "still open"。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

完成 task012。

设计选择：Super3 ship 独立 `super3.jinja` (verbatim copy of nano3 + 2 行 header) 而非 resolver alias。理由是配置文件的依赖意图更显式，未来 diverge 时不动 resolver；配套的 body-byte-identity 测试在意外漂移时会响。

实现：

- `src/nemotron/data_prep/templates/super3.jinja`：214 行 (2 行 jinja 注释 + 212 行 nano3 body)。
- `src/nemotron/data_prep/core/chat_sft_shard_core._apply_chat_template`：抽 `_BUILTIN_TEMPLATES = {"nano3", "super3"}`，两者走同一段加载逻辑。
- `stage1_sft/config/data_prep/{default,agentic_v0,tiny}.yaml`：`chat_template: nano3` → `super3`，三处 TODO/comment 一并更新。
- `run_m1_sft_roundtrip_smoke.py`：`NANO3_TEMPLATE` 常量 → `SUPER3_TEMPLATE`；docstring 同步。
- `tests/data_prep/test_chat_template_super3.py`：4 个 case
  - `test_apply_chat_template_resolves_super3_name` (gated by `pytest.importorskip("pydantic")`, NemTron 有)
  - `test_super3_template_renders_four_role_conversation` — system → user → assistant w/ tool_calls → tool 四角色 render；boundary tokens 顺序对齐。第一版用 `rendered.index("<tool_call>")` 抓到了 system block 里的 format example，改成从 `<|im_start|>assistant` 之后 search 真正的 assistant tool call。
  - `test_super3_template_keeps_escaped_tool_markup_as_quoted_text` — task005 (`905de2d`) `escape_tool_markup_for_prompt` 链路保护 ：转义后的 `&lt;tool_call&gt;` 不能被 Jinja 解读成真 tool call。
  - `test_super3_body_is_currently_verbatim_copy_of_nano3` — strip 头部 jinja 注释后 body 必须 byte-identical；diverge 时主动失败提醒人。
- 文档：REVIEW_v0.md #8 翻 ✓；`docs/implementation-roadmap.md` §1.2 / §5 critical path / §7.1 open question 一起更新；`m1_agentic_sft/README.md` / `data_prep/README.md` / `m0-dataset-expansion-plan.md` §1.1 把 "Nano3 chat template" → "Super3 chat template"。

测试：sandbox 没 transformers / pyarrow，因此 M1 test 文件 collection 失败、template resolver test pydantic-skip；但 `tests/data_prep/test_chat_template_super3.py` (4 cases — 3 passed + 1 skipped) + `tests/recipes/super3/test_m0_data_env.py` + `test_m0_health_baseline.py` 全过 (46 passed + 1 skipped)。NemTron 上能跑完整 pytest。

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

PR #28 已 squash-merge 为 `04681a7`。intern status 回 Idle (Session 16)。task012 结题；REVIEW_v0.md 维度上 #8 翻 ✓ 后剩 1 个 still-open 设计类 (#9 two-stage SFT loss → task013)，其余 critical path 进入 task021 (M1 infra minimum)。
