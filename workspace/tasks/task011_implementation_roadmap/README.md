# task011_implementation_roadmap

<!-- METADATA:STATUS=Done,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

task001 → task010 把 M0 + M1 Agentic SFT v0 review 全部 follow-up 都合入了 main：REVIEW_v0.md 状态 **17 fixed / 1 partial / 2 still-open (#8 chat template、#9 two-stage loss — design 类) / 2 tracked (task005)**。

但 plan 文档 (`docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md`) 描述的 scope 远超已落地范围：

- M1 RL (RLVR 1/2/3、SWE1、SWE2、RLHF、eval gate) 全部都只有 stage2/3 config scaffold + 一份 16K 的 data_prep.py，没有跟 M0/M1 SFT 接通。
- M2 (35-50 envs、SFT v1、curriculum、rollout store、judge pool、shadow eval、env health dashboard) 整段空白。
- M3 (70-100+ envs、SFT v2、3-wave RL、1K-GPU async GRPO、sandbox pool、replay UI、promotion gate、quantization serving、checkpoint freeze) 整段空白。
- W1 unified data registry、W1 difficulty curriculum sampler、W1 failure-rollout-to-SFT-repair pipeline、W2 env telemetry emitter、W2 per-env shadow split 也都没动。

没有一份能串起 "plan -> 已落地 -> 剩余差距 -> 任务编号" 的索引文档。当前只能反向地从 git log + REVIEW_v0.md + 各 task 工作区拼凑全貌。

## 目标

把 plan 文档的每一节按 milestone (M1 / M2 / M3) + workflow (W1-W5) 与当前主干代码状态做逐条 gap 分析，落成 `docs/implementation-roadmap.md`，对每个差距挂一个建议任务编号 (task012–task055)，并标注 priority、依赖、acceptance criteria。

文档要：

- 沿用 plan 文档的章节锚点 (§3 / §5 / §6 / §7 / §8 / §9 / §10 / §11 / §12)，方便交叉查阅。
- 沿用 REVIEW_v0.md 的 ✓ / ◐ / ✗ / 📋 legend。
- 给出明确的 8-PR critical path 排序，按依赖串成单线 (M1 → 部分 parallel)。
- 列出 7 个尚未拍板的 open question，每个 question 对应阻塞的 task 编号。
- 配 risk → mitigation hook 映射 (对齐 plan §12)。

不动任何代码。

## 验收

- [x] 创建 `docs/implementation-roadmap.md`，覆盖 M1 / M2 / M3 全部 milestone scope。
- [x] 每个 gap 项至少有：plan reference + 当前 status + 缺什么 + suggested taskNNN 编号 + acceptance criteria。
- [x] 任务编号从 task012 开始，与 task011 (本 PR) 不冲突；最高编号 task055。
- [x] Critical path 列出 8 个 PR 顺序；其中 task020 (M1 infra) 是后续大部分依赖的前置。
- [x] 与 REVIEW_v0.md 交叉引用 (#8 / #9 / #14 / #21 等 finding 编号)。
- [x] 不修改 plan 文档本身。

## 参考文件

- `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` — plan 文档原文 (719 lines)。
- `docs/multi-environment-rl-post-training-plan.md` — 同份 plan 的英文版精简版。
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/REVIEW_v0.md` — review v7 终态，task001-009 修复 status 表。
- `src/nemotron/recipes/super3/stage2_rl/` — stage2 RLVR/SWE1/SWE2/RLHF config scaffold (data 全无 M0/M1 wiring)。
- `src/nemotron/recipes/super3/stage3_eval/config/default.yaml` — eval scaffold (203 lines, 无 benchmark adapter)。
- `workspace/tasks/task005_m1_sft_v0_scope_expansion/README.md` — 已经登记的 v0 scope expansion task，本 roadmap 把它放在 critical path #1。
