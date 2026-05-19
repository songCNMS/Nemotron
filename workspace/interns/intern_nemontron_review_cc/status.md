# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task030_unified_data_registry -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task030_unified_data_registry |
| PR | pending push |
| Session | 49 |

正在做：task030 Session 5 — share-alike license cascade audit (task058
license/contamination 主题 follow-up)。把 `docs/m0-dataset-expansion-plan.md`
§6 Q1 的 share-alike prose policy 翻成机器可查 audit。

- 新模块 `data_registries/license_audit.py` 含 `SHARE_ALIKE_LICENSE_PREFIXES`
  (cc-by-sa / gpl / agpl / lgpl / odbl) + `is_share_alike` predicate +
  `find_share_alike_sources` + `license_cascade` (带 `live_chains` 计数
  区分 live vs latent) + `format_cascade_report` 文本渲染
- `scripts/validate_data_registries.py` 加 `--license-cascade` flag：
  audit-only mode，短路 schema validation，exit 0 即使有 finding (informational)

Live audit finding: HotpotQA (cc-by-sa-4.0) 是 latent — task015 删了
`search_grounded_qa` NeMo-Gym 错名 mapping，没 bridge 行 reference 该
m0_env。一旦未来 wire 上，audit 翻 LIVE 提醒重审 §6 Q1。

27 个新 pytest case；sandbox 测试基线 233 → 260 passed + 6 skipped。
`docs/m0-dataset-expansion-plan.md` §6 Q1 加段落指向新 CLI flag。
