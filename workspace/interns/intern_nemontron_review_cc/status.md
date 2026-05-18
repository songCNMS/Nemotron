# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 36 |

最近：task030 Session 1 (PR #48 `ec1b271`) 已 squash-merge 进 main —
unified data registry schema 层 + 索引。新模块
`src/nemotron/recipes/super3/milestones/data_registries/` 含 schema.py
(5 个 kind 的 row validator + KNOWN_BRIDGE_STATUSES 跟 _bridge_base 双
向独立 + pytest 强制对齐) + unified_index.yaml (8 个 registry 一行
entry) + unified_index_loader.py (validate + 三个 read-only inventory
walk: licenses / hf_dataset / m0_to_downstream)。决策：layer 不 merge
— 8 个 registry 真文件原地不动，schema 层叠在上面。Live unified index
全过 validation。19 个新 pytest case，sandbox 测试基线 129 → 148
passed + 2 skipped。

task030 整 task 仍 InProgress：Session 2 (M1 eval basket registry
等 task019 / task020；schema enforcement at write time；8 个
module-local loader 接进 schema 层) 待开。

下一个候选 (按 sandbox-runnable + leverage 排序)：

- 之前 task 的 Session 2+ 大都需 cluster / Docker / nvcr container：
  - **task013 Session 2** — 两阶段 SFT loss driver + cluster verify
  - **task014 Session 2** — RLVR1 config wiring + smoke launcher
  - **task016 Session 2** — M0 SWE pivot converter (SWE-Gym / R2E)
  - **task017 Session 2** — OpenHands wrapper + watchdog
  - **task018 Session 2** — HelpSteer-2 M0 converter
- **task019 / task020** — M1 eval basket (block on task014 Session 2 真 RLVR checkpoint；本身设计 sandbox-runnable)
- **task056 Session 2** — math_formal_lean (法务 share-alike clearance)
- **task021 Session 3-4** — sandbox container 构建 / cluster verify
