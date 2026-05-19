# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task030_unified_data_registry -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task030_unified_data_registry |
| PR | pending push |
| Session | 43 |

正在做：task030 Session 2 — schema enforcement at write time。Session 1
落了 validator + 索引 + inventory；本 session 把 validator 包成 CLI +
pre-commit hook。

- 新 `scripts/validate_data_registries.py` (退出码 0/1/2 区分 clean /
  drift / infra-broken；`--quiet` / `--paths` / `--index-path` flags)
- `.pre-commit-config.yaml` 加 local hook `validate-data-registries`，
  trigger on registry YAML / loader / schema / script 变动
- 决策：**不**合并 bridge runtime fail-fast 跟 schema collect-all
  层 — 两层 consumer 不一样

11 个新 pytest case (script file shape / clean-main / broken-index
subprocess / `--paths` / missing index / in-process main / pre-commit
config validation)。Sandbox 测试基线 204 → 215 passed + 6 skipped。
Session 3 (M1 eval basket — block on task019/020) + Session 4 (loader
merge) carry over。
