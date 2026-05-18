# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 32 |

最近：task013 Session 1 (PR #44 `10e1393`) 已 squash-merge 进 main —
plan §5.1 / REVIEW #9 两阶段 SFT loss 的基建。新增 `sample_level_loss.py`
(纯 torch helper) + `sample_level_step.py` (Megatron-Bridge forward_step
adapter) + `step_dispatch.py` (独立 `_STEP_FUNCTIONS` 注册表) + `train.py`
接入 `step_function` YAML key (默认 `gpt_step` → 现有 YAML 字节级同行为)。
12 新 pytest case，sandbox 测试基线 125 → 129 passed + 2 skipped。REVIEW
#9 ✗ → ⚠ (cluster verify Session 2)。

**里程碑**: roadmap §5 critical-path **所有 9 条** Session 1 全部落地 ✓:

| # | Task | Session 1 PR |
|---|---|---|
| 1 | task005 | (pre-existing) |
| 2 | task012 | PR #28 |
| 3 | task021 | PR #30 / #32 |
| 4 | task014 | PR #34 |
| 5 | task015 | PR #36 |
| 6 | task016 | PR #38 |
| 7 | task017 | PR #40 |
| 8 | task018 | PR #42 |
| 9 | task013 | PR #44 |

下一个候选 (按 sandbox-runnable + leverage 排序):

- **task017 Session 4** — `_bridge_base.py` 抽取 (4 个 bridge module 都摆稳：RLVR + SWE1 + SWE2 + RLHF)
- **task030** — unified data registry (across-M2 cleanup)
- **task019 / task020** — M1 eval basket (block on task014 Session 2 真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都要 cluster 或 HF 下载，sandbox 跑不了
