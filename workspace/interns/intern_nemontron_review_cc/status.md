# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task017_m1_swe2_sandbox_runtime -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task017_m1_swe2_sandbox_runtime |
| PR | pending push |
| Session | 33 |

正在做：task017 Session 4 — `_bridge_base.py` 抽取。RLVR + SWE1 + SWE2 +
RLHF 四个 bridge module 80% 代码重复，等四个 module 都摆稳后做这个
refactor。新文件 `src/nemotron/recipes/super3/milestones/_bridge_base.py`
含 JSONL/JSON helpers / discover_m0_split_files / status vocabulary /
generic load_env_registry (带 extra_row_validator hook) / derive_env_map /
base_coverage_report / base_tag_record / collect_mix_rows。Module-
specific 留在 prep script：mix name、注册表路径、prepare() 主流程、
SWE2 sif_source / RLHF pref_dataset 扩展字段、coverage 扩展。行数：
2121 → 1901 (-220 净减；4 个 prep script 各砍 130-190 行；新增 387 行
共享 base)。零行为变化，129 passed + 2 skipped 跟 refactor 前基线
一致。
