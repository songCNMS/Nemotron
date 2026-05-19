# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task030_unified_data_registry -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task030_unified_data_registry |
| PR | pending push |
| Session | 47 |

正在做：task030 Session 4 — bridge / M0 module-local loader 接进 schema 层。

**正确合并粒度**: 合并 row-shape *definitions*（单 source of truth in
`schema.py`），不合并 aggregation *behavior* (`fail_fast` vs collect-all
分别给 runtime vs audit consumer)。Session 1+2 的 "不合并" 决策 update
成 "合并 schema，保留 dual aggregation mode"。

具体改动:

- `schema.validate_rows` 加 `fail_fast=False` + `source_path=None` 参数
- `schema.validate_top_level` 加 `strict=True` 参数 (False 跳 schema_version /
  milestone, runtime loader 用)
- Error message 格式统一成 `<rows_key>[<index>] missing required field`
- 4 个 runtime loader (`_bridge_base.load_env_registry` /
  `m1_swe2.load_swe2_sif_registry` / `m1_rlhf.load_rlhf_pref_data_registry` /
  `sandbox_containers.image_resolver.load_sandbox_image_registry`) refactor 成
  schema 委派 + module-specific 检查包成 `extra_validators` closure

**关键不变量守住**: 没动任何模块测试文件，所有 226 个原测试照过。新加
7 个 schema API surface tests (fail_fast 短路 / source_path 前缀 /
collect-all 完整 list / strict=True/False 行为 / known statuses 双向对
齐) lock 住 Session 4 的 API 契约。

测试基线 226 → 233 passed + 6 skipped (7 new).

task030 整 task 仍 InProgress：Session 3 (eval basket — block on
task019/020) 待开。
