# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task030_unified_data_registry -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task030_unified_data_registry |
| PR | pending push |
| Session | 51 |

正在做：task030 Session 6 — HF revision-pin lint (task058 license/
contamination 主题 follow-up，配 Session 5 share-alike audit)。

- 新模块 `data_registries/revision_audit.py` (`FLOATING_REVISION_REFS`
  frozenset + `is_pinned` predicate + `find_unpinned_revisions` →
  blockers / informational 双 bucket + `format_revision_audit_report`)
- `scripts/validate_data_registries.py` 加 `--check-revision-pins` flag：
  exit 1 if any blocker (CI gate)；informational only → exit 0
- `.pre-commit-config.yaml` 加 `check-revision-pins` local hook，并行
  Session 2 的 `validate-data-registries`

Live audit 今天：0 blockers + 3 informational (HelpSteer-2 /
UltraFeedback / Orca DPO pairs 候选等 task018 Session 2 pin)。

33 个新 pytest case (31 audit + 2 hook config)；sandbox 测试基线 260
→ 293 passed + 6 skipped.

task030 整 task 仍 InProgress：Session 3 (eval basket — block on
task019/020) 待开。
