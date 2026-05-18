# task_knowledge

<!-- METADATA:SESSION=1 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### Roadmap 任务编号的留白规则

`docs/implementation-roadmap.md` 把后续 implementation task 占位编号到 task012–task055。已落地或正在用的编号：

- task001 / task002 — M0 review 修复 (已合)
- task003 — M1 SFT v0 review report (已合)
- task004 / task006 / task007 / task008 / task009 / task010 — task003 的 follow-up 修复 (已合)
- task005 — M1 SFT v0 scope expansion (terminal / structured / short SWE / negatives)，仍 Todo
- task011 — 本 PR (roadmap doc)

下一个能直接拿编号的 implementation task 是 **task012** (Super3 chat template)。再往后顺序见 `docs/implementation-roadmap.md` §5 critical path。

如果决定新开一个 "review / housekeeping / docs only" task，可以在当前已用编号之外另起 (e.g. task200+)，避免再次像 task011 这样跟 implementation 占位冲突。

### task011 与 plan 文档的解耦

`docs/implementation-roadmap.md` **不修改** `docs/multi-environment-rl-post-training-plan.zh.text-agentic-only.md` 任何内容。后者是 product / 立项时冻结的 plan，前者是 engineering 状态视图，两份分开维护：

- 改 scope / target / acceptance → 改 plan。
- 改实现顺序 / 任务编号 / 当前 status → 改 roadmap。

REVIEW_v0.md 是同思路 (v1 review 内容冻结，v2-v7 status 表追加在前面)，复用同一约定可以减少未来跨文档同步成本。
