# task030 - task_knowledge

## 8 个 registry 今天的 shape

| Path | Kind | Rows key | Required row fields |
|---|---|---|---|
| `m0_data_env/data_registry.yaml` | m0_data_registry | datasets | id, environment, hf_dataset, hf_split, hf_revision, license, converter, use_stage |
| `m0_data_env/environment_registry.yaml` | m0_environment_registry | environments | id, family, stage, input_schema, reward, telemetry, health_check |
| `m1_rlvr/rlvr_env_registry.yaml` | bridge_env_registry | envs | nemo_gym_env, mix, status |
| `m1_swe1/swe1_env_registry.yaml` | bridge_env_registry | envs | (同上) |
| `m1_swe2/swe2_env_registry.yaml` | bridge_env_registry | envs | (同上 + sif_source 字段 optional) |
| `m1_swe2/swe2_sif_registry.yaml` | sif_registry | sif_sources | source, filename_template |
| `m1_rlhf/rlhf_env_registry.yaml` | bridge_env_registry | envs | (同上 + pref_dataset_candidate 字段 optional) |
| `m1_rlhf/rlhf_pref_data_registry.yaml` | pref_data_registry | datasets | id, hf_dataset, license |

Top-level 每个 registry 都要 `schema_version`, `milestone`，加 rows key。

## 决策：layer 不 merge

Plan §6 W1 写的是 "merge M0 yaml format, extend with RL/eval fields"。
直接读上面这条建议是合并 8 个 yaml 到一个大 yaml；Session 1 决定不这
么做，理由：

1. **Module boundaries**：M0 / m1_rlvr / m1_swe1 / m1_swe2 / m1_rlhf
   各自的 prep script 就近读自己的 yaml 是天然好结构。合并要么
   破坏 import 路径，要么让每个 prep script 都去读巨大共享 yaml 再过
   滤——前者破坏 isolation，后者性能 + 可读性都差。
2. **Diff & 评审**：合并后任何 registry 改动都在同一个文件 diff；
   reviewer 看 RLHF pref 改动要翻过 RLVR 21 行 env、SWE2 SIF 3 行、
   M0 11 行 dataset。
3. **Schema drift**：层化设计强行解耦——`data_registries/schema.py`
   是单一来源 of "什么 kind 应该有什么字段"，registry 真文件 fail
   时 schema 层告诉你 expected 是什么。merge 把 schema 跟数据混在一
   起，drift 反而更容易。

所以 Session 1 上面**叠一层** schema + 索引 + cross-registry inventory：

```
            unified_index.yaml (catalog)
                  ↓ kind, path
        data_registries/schema.py (per-kind shape)
                  ↓ validate
   ┌─────────────┼─────────────┐
   M0 yamls   M1 bridge yamls   M1 secondary yamls
   (existing — unchanged)
```

## Inventory walks (operator-facing)

三个 read-only walk 跑 sandbox 都过：

| Walk | 返回 | Use case |
|---|---|---|
| `licenses_inventory()` | `{license: [{registry_id, kind, row_id}]}` | 法务 audit "cc-by-sa-4.0 在哪些 row 出现" |
| `hf_dataset_inventory()` | `{hf_dataset: [{revision, pin_required, license}]}` | Release gate "哪些数据没 pin revision" |
| `m0_to_downstream_inventory()` | `{m0_env_id: [{registry, mix, status}]}` | Planning "如果加 M0 env X，哪些 mix 自动 light up" |

## extra_row_validator 钩子

`schema.validate_rows(...)` 接 `extra_validators: Iterable[Callable]`。
每个 validator 接 `(row, index)` 返回 None (pass) 或 str (issue
description)。`unified_index_loader` 给 bridge_env_registry 默认套两
个 validator:

1. `bridge_status_validator` — status 必须在 `KNOWN_BRIDGE_STATUSES`
2. `bridge_mix_validator_factory(expected_mixes)` — 如果 index 行
   declare 了 `expected_mixes`，row 的 mix 必须在其中

后者特别重要 — 它把 "rlvr1 行不能放在 swe1 registry" 这种 copy-paste
bug 从 bridge runtime 校验提升到 schema 层。`m1_swe1/prepare_*` 自己
也有这个校验 (`_bridge_base.load_env_registry(expected_mix=...)`)，但
那是 runtime 校验；schema 层让 audit 跑测试时就发现。

## KNOWN_BRIDGE_STATUSES 双向独立

`schema.py` 不 import `_bridge_base` — 在自己的层声明 `KNOWN_BRIDGE_STATUSES`。
然后 pytest `test_known_bridge_statuses_match_bridge_base` 用 assert
让两层 frozenset 必须相等。Drift 由测试发现，不靠 import 强绑定。这
样：

1. `data_registries/` 模块不依赖 bridge runtime — 单独可用 (audit
   工具能在不装 megatron-bridge 的 sandbox 跑)
2. Bridge runtime 不依赖 schema 层 — 也单独可用 (现有 4 个 prep
   script 不需要 import schema)
3. 任何一方加新 status 都要改两个文件 — 强制审视另一方有没有跟着改

## Session 2 候选 work items

1. **Eval basket registry** (block on task019)：
   - 新增 kind `eval_basket_registry`
   - `unified_index.yaml` 加一行
   - schema.py 加 row fields (benchmark_id, adapter, hf_dataset, license,
     promotion_gate)
   - `eval_basket_inventory()` walk

2. **Schema enforcement at write time**：
   - Pre-commit hook：`validate_unified_index()` 跑过才能 commit
   - Pre-PR hook (CI)：同上
   - Bridge runtime 接 schema 层：让 `_bridge_base.load_env_registry`
     调用 `schema.validate_rows` 而不是自己重写校验

3. **Auto-fix tooling**：
   - 找出 hf_revision 缺 pin 的 dataset，建议拉最新 commit
   - 找出 license 字段为 `<unknown>` 的 row，blocker 标出

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| `data_registries/` 模块 | yes |
| schema 校验 + index load + inventory walk | yes |
| Session 2 eval basket | yes (但需要 task019 先把 eval registry 写好) |
| Schema enforcement (commit hook) | yes |
| 真集群跑数据 prep | no (但不归本 task) |

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，pre-existing；非 sandbox 正常跑。
