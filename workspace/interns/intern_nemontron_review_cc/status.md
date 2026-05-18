# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 34 |

最近：task017 Session 4 (PR #46 `5943e18`) 已 squash-merge 进 main —
`_bridge_base.py` 抽取。RLVR + SWE1 + SWE2 + RLHF 四个 registry-driven
bridge module 共享 scaffolding (JSONL helpers / discover_m0_split_files
/ status vocabulary / load_env_registry / derive_env_map /
base_coverage_report / base_tag_record / collect_mix_rows)。零行为变化，
129 passed + 2 skipped 跟 refactor 前一致。行数 2121 → 1901 (-220 净；
607 行重复合到 387 行共享 base)。Module-specific 留在各 prep script
(mix name / prepare 主流程 / SWE2 sif_source / RLHF pref_dataset)。

task017 整 task 仍 InProgress：Session 2 (OpenHands wrapper + SWE-Gym
converter + watchdog) / Session 3 (cluster smoke + Docker fallback)
待开 — 都需 cluster / Docker。

下一个候选 (按 sandbox-runnable + leverage 排序):

- **task030** — unified data registry (across-M2 cleanup; 把 M0
  `data_registry.yaml` + RLHF pref_data registry + SWE2 SIF registry
  + RLVR env_registry 统一抽 schema)
- **task019 / task020** — M1 eval basket (block on task014 Session 2
  真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都要 cluster 或 HF 下载，sandbox 跑不了
