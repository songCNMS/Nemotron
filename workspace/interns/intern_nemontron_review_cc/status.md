# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 52 |

最近：task030 Session 6 (PR #65 `db8900d`) 已 squash-merge 进 main —
HuggingFace revision-pin lint (task058 license/contamination 主题
follow-up)。新模块 `data_registries/revision_audit.py` +
`scripts/validate_data_registries.py --check-revision-pins` flag +
`.pre-commit-config.yaml` `check-revision-pins` hook。Live audit 今天 0
blockers + 3 informational (pref data candidates 等 task018 Session 2
pin)。33 个新 pytest case，sandbox 测试基线 260 → 293 passed + 6 skipped。

task030 整 task 仍 InProgress：Session 3 (M1 eval basket — block on
task019/020) 待开。

下一个候选 (sandbox-runnable):
- **task058 follow-ups 剩下** — 更严的 `contamination_against` 校验
  (e.g., gsm8k 行必须 mention "GSM8K test" / 数学源必须 mention 常见
  math eval baskets) — 把 schema-level required_row_fields 检查升级到
  semantic content 检查
- **task019 / task020** — M1 eval basket (本身 sandbox-runnable；acceptance
  要真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都需 cluster / Docker / nvcr container
