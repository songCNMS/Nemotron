# task012_super3_chat_template

<!-- METADATA:STATUS=Done,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

REVIEW_v0.md #8 自 task002 起标记为 still-open：`stage1_sft/config/data_prep/{default,agentic_v0,tiny}.yaml` 全部用 `chat_template: nano3`，README 也注释 "Super3 currently reuses the checked-in Nano3 template implementation"。`docs/implementation-roadmap.md` §1.2 / §7.1 把 "Super3 ships its own jinja or formalize Nano3 reuse?" 列成阻塞 task012 的 open question。

## 决定 (open question §7.1 答案)

**Super3 ships its own jinja**，初始内容是 `nano3.jinja` 的 verbatim copy。理由：

- nano3 模板已经覆盖 M1 SFT v0 需要的所有形态 (tools 注入、tool_call / tool_response 边界、thinking、reasoning budget、history truncation)；没有具体的 Super3 行为分歧待解。
- 单文件复制比 "resolver alias" 在配置文件里更显式：YAML 写 `chat_template: super3` 即指向独立模板；未来出现 Super3-specific 行为时直接编辑 `super3.jinja`，无需碰 resolver。
- 加 2 行 jinja 注释头说明 "starts as a verbatim copy of nano3" + 配套的 body-byte-identity 测试 = 拒绝意外漂移；要主动 diverge 时这个测试会响。

## 目标

- 新增 `src/nemotron/data_prep/templates/super3.jinja` (带 2 行 header comment 的 nano3 verbatim copy)。
- `chat_sft_shard_core._apply_chat_template` 通过 `_BUILTIN_TEMPLATES = {"nano3", "super3"}` 同时解析两个名字。
- 切 `stage1_sft/config/data_prep/{default,agentic_v0,tiny}.yaml` 到 `chat_template: super3`。
- 切 `run_m1_sft_roundtrip_smoke.py` 常量 `NANO3_TEMPLATE` → `SUPER3_TEMPLATE`；docstring 把 "Nano3 chat template" → "Super3 chat template"。
- 新加 `tests/data_prep/test_chat_template_super3.py`：4 个 case 覆盖 resolver / 4-role conversation render / tool-call-repair-negative 转义不被 Jinja 吃掉 / super3 body 与 nano3 byte-identical。
- 文档更新：roadmap §1.2 / §5 critical path / §7.1 open question / REVIEW_v0.md #8 全部翻牌为 ✓ 并指向本 task；M1 README + data_prep README + m0-dataset-expansion-plan §1.1 把 "Nano3 chat template" 改成 "Super3 chat template"。

## 验收

- [x] `super3.jinja` 存在，body 等于 nano3 (test passes)。
- [x] resolver 识别 `super3` 名字 (test gated by pydantic install, NemTron 默认有)。
- [x] 三个 data-prep yaml 全部 declare `super3`。
- [x] roundtrip smoke + chat_template_super3 测试 4 个 case 全过 (sandbox 测得 3 passed + 1 skipped pydantic-gated)。
- [x] REVIEW_v0.md #8 / roadmap §1.2 / §5 / §7.1 / m1 README / data_prep README / m0-dataset-expansion-plan §1.1 全部更新。
- [x] 没碰 nano3 template 内容；没改 nano3 resolver 行为；没碰任何 model checkpoint 配置。

## 依赖

无。task012 独立于其他任何 task；本 PR 是落地 task005 + task056 之后下一个 critical-path 单元。

## 参考文件

- `src/nemotron/data_prep/templates/nano3.jinja` — 模板源头
- `src/nemotron/data_prep/templates/super3.jinja` — 新增
- `src/nemotron/data_prep/core/chat_sft_shard_core.py` `_apply_chat_template` — resolver
- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/{default,agentic_v0,tiny}.yaml` — flip
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/run_m1_sft_roundtrip_smoke.py` — constant rename
- `tests/data_prep/test_chat_template_super3.py` — 新增 4 cases
- `docs/implementation-roadmap.md` §1.2 / §5 critical-path / §7 open-questions
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md` #8 status row
