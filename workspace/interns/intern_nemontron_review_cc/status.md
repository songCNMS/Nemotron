# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 44 |

最近：task030 Session 2 (PR #57 `324e062`) 已 squash-merge 进 main —
schema enforcement at write time。新 `scripts/validate_data_registries.py`
(退出码 0/1/2 区分 clean / drift / infra-broken；`--quiet` / `--paths` /
`--index-path` flags) + `.pre-commit-config.yaml` local hook
`validate-data-registries` (trigger on registry YAML / loader / schema /
script 变动)。设计决策：**不**合并 bridge runtime fail-fast 跟 schema
collect-all，两层 consumer 不一样。11 个新 pytest case，sandbox 测试
基线 204 → 215 passed + 6 skipped。

task030 整 task 仍 InProgress：Session 3 (M1 eval basket — block on
task019/020) + Session 4 (Bridge/M0 loader merge into schema layer —
注意 fail-fast vs collect-all 语义) 待开。

下一个候选 (sandbox-runnable + leverage):
- **task058 follow-ups** — license/contamination 额外校验加进 schema 层
  (e.g., share-alike cascade 检测，CC-BY-SA 数据流到哪些 derived artifact)
- **task021 Session 6 候选** — RLVR rollout default `container_runtime`
  从 `None` 翻 `"docker"` (production behavior flip 独立 PR)
- **task030 Session 4** — Bridge / M0 module-local loader 接进 schema 层
  (careful refactor，runtime fail-fast 不能 break)
- **task019 / task020** — M1 eval basket (block on task014 Session 2 真 RLVR checkpoint)
- 之前 task 的 Session 2+ — 大都需 cluster / Docker / nvcr container
