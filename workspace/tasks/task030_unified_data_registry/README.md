# task030_unified_data_registry

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #48 / ec1b271 on 2026-05-18 -->
<!-- SESSION 2 LANDED: PR #57 / 324e062 on 2026-05-18 (schema enforcement script + pre-commit hook) -->
<!-- SESSION 4 LANDED: PR #61 / 159d81f on 2026-05-18 (bridge / M0 module-local loader merge into schema layer) -->
<!-- SESSION 5 LANDED: PR #63 / 028f377 on 2026-05-19 (share-alike license cascade audit — task058 license/contamination follow-up) -->
<!-- SESSION 6 LANDED: PR pending on 2026-05-19 (HuggingFace revision-pin lint — task058 follow-up) -->

## 背景

Plan §6 W1 / roadmap §3 W1 row：

> 跨 SFT + RL + Eval 的 unified data registry

今天 Super3 pipeline 8 个 registry YAML 散在 5 个目录：

| Path | Kind | Author |
|---|---|---|
| `m0_data_env/data_registry.yaml` | M0 11 HF datasets | M0 baseline |
| `m0_data_env/environment_registry.yaml` | M0 11 reward envs | M0 baseline |
| `m1_rlvr/rlvr_env_registry.yaml` | RLVR1/2/3 21 NeMo-Gym envs | task015 Session 1 |
| `m1_swe1/swe1_env_registry.yaml` | SWE1 single env | task016 Session 1 |
| `m1_swe2/swe2_env_registry.yaml` | SWE2 三 SIF family | task017 Session 1 |
| `m1_swe2/swe2_sif_registry.yaml` | SWE2 SIF filename templates | task017 Session 1 |
| `m1_rlhf/rlhf_env_registry.yaml` | RLHF 两 envs | task018 Session 1 |
| `m1_rlhf/rlhf_pref_data_registry.yaml` | RLHF 候选 pref data 3 个 | task018 Session 1 |

每个都有自己的 loader + validator，shape 一致但 schema 没共享。Plan §6
W1 想要"merge M0 yaml format, extend with RL/eval fields"。

**Session 1 决策**：不真合并 — 而是上面叠一层 schema + 索引。Module
boundaries 保留，每个 registry 留在自己的目录；新加一个
`data_registries/` 模块做 cross-cutting validation + inventory walk。
合并文件会破坏 module 自治（M0 / m1_* 各自的 prep script 还会就近读
自己那份 yaml），还会让 git diff 难看。叠 schema 层成本低 + 拿同样收益。

整 task 拆 Sessions：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | Schema 层 + unified index + 三个 cross-registry inventory walk | yes | ✓ Done (this PR) |
| 2 | Schema enforcement at write time (`scripts/validate_data_registries.py` + `.pre-commit-config.yaml` local hook) | yes | ✓ Done (this PR) |
| 3 | M1 eval basket registry (kind + index row + schema validator) | yes (sandbox) | Todo (block on task019 / task020 给 eval basket 真定义) |
| 4 | Bridge / M0 module-local loader 接进 schema 层 merge 两层校验逻辑 — *单 source of truth* for row shape, fail-fast / collect-all 语义保留 | yes | ✓ Done (PR #61) |
| 5 | Share-alike license cascade audit (`data_registries/license_audit.py` + `--license-cascade` CLI flag) — task058 license/contamination follow-up; converts §6 Q1 share-alike prose policy into machine-checkable | yes | ✓ Done (PR #63) |
| 6 | HuggingFace revision-pin lint (`data_registries/revision_audit.py` + `--check-revision-pins` CLI flag + pre-commit hook) — task058 follow-up; m0_data_registry unpinned → blocker exit 1; pref_data_registry candidates → informational exit 0 | yes | ✓ Done (this PR) |

## Session 1 目标

新模块 `src/nemotron/recipes/super3/milestones/data_registries/`:

1. **`schema.py`** — 每个 registry kind 一个 dataclass-style validator：
   - `m0_data_registry` (datasets: id / hf_dataset / hf_revision / license / converter / use_stage)
   - `m0_environment_registry` (environments: id / family / reward / telemetry / health_check)
   - `bridge_env_registry` (envs: nemo_gym_env / mix / status；通用，4 个 M1 bridge 都用)
   - `sif_registry` (sif_sources: source / filename_template)
   - `pref_data_registry` (datasets: id / hf_dataset / license)
   - `KNOWN_KINDS` frozenset / `KNOWN_BRIDGE_STATUSES` (跟 `_bridge_base.KNOWN_STATUSES` 同步)
   - `bridge_status_validator` / `bridge_mix_validator_factory` 接 `extra_row_validator` 钩子

2. **`unified_index.yaml`** — meta-registry，每行 declare 一个真 registry:
   - 8 个 entries 对应今天 8 个 registry
   - 字段：`id`, `kind`, `path`, `summary`, `produced_by`, `consumed_by`, `expected_mixes` (bridge_env_registry only)
   - 加 task019 eval basket 就一行

3. **`unified_index_loader.py`** —
   - `load_unified_index()` 解析 + 校验 meta-registry
   - `validate_unified_index()` 对每个被引用的 registry 跑 kind-appropriate schema
   - 三个 sandbox-runnable inventory walk:
     - `licenses_inventory()` — `{license: [(registry_id, kind, row_id)]}`
     - `hf_dataset_inventory()` — `{hf_dataset: [{revision, pin_required, license, ...}]}`
     - `m0_to_downstream_inventory()` — `{m0_env_id: [{registry, mix, status, ...}]}`

## Session 1 验收

- [x] `data_registries/` 模块 + 三个文件 (`schema.py` / `unified_index.yaml` / `unified_index_loader.py`)
- [x] `schema.KNOWN_KINDS` 覆盖今天的 5 个 kind
- [x] `schema.KNOWN_BRIDGE_STATUSES` 跟 `_bridge_base.KNOWN_STATUSES` 双向对齐 (pytest)
- [x] `unified_index.yaml` 列今天全部 8 个 registry
- [x] `validate_unified_index()` 在 live main 跑 clean (issues == [])
- [x] 每个 registry path 真存在 (pytest)
- [x] `licenses_inventory()` 找到 cc-by-4.0 / apache-2.0 / mit 等已知 license
- [x] `hf_dataset_inventory()` 列 M0 数据 + RLHF pref data 候选；revision pin 状态正确
- [x] `m0_to_downstream_inventory()` 找到 active 路径 (math_reasoning_numeric → rlvr1, structured_outputs_json → rlvr2)
- [x] 三个 inventory walk 是 read-only (mtime 不变)
- [x] 至少 19 个 pytest case
- [x] Roadmap §3 W1 row + §5 critical-path 加 Session 1 ✓

## 依赖

- 不依赖 cluster / Docker / W&B / HF
- 不依赖 _bridge_base.KNOWN_STATUSES (仅在 pytest 对齐时引用一次)
- 不破坏现有 8 个 registry 的 loader — 它们继续用自己的 module-local validator

## Session 2+ 不在本 PR

- task019 / task020 落地后加 `eval_basket_registry` kind + 一行 index
- Pre-commit / pre-PR hook 自动跑 `validate_unified_index()` 拦下 shape drift
- 把 module-local loader (e.g., `m1_rlvr/prepare_m1_rlvr_jsonl.load_rlvr_env_registry`)
  改用 schema 层做 validation (今天是 module 自己写校验逻辑，跟 schema 层重复)

## 参考文件

- `src/nemotron/recipes/super3/milestones/data_registries/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/_bridge_base.py` — bridge runtime side
- `src/nemotron/recipes/super3/milestones/m0_data_env/{data,environment}_registry.yaml`
- `src/nemotron/recipes/super3/milestones/m1_*/yaml` — 4 个 bridge + 2 个 secondary registry
- plan §6 W1 + roadmap §3 W1 row + §5 critical-path
