# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 plan §6 W1 派生：跨 SFT + RL + Eval 的 unified data registry。今天 8
个 registry YAML 散在 5 个目录，每个有自己的 loader。Session 1 决定不
合并文件 — 上面叠一层 schema + 索引 + cross-registry walk。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 schema 层 + unified index + 三个 inventory walk。设计:

- 新模块 `src/nemotron/recipes/super3/milestones/data_registries/`，
  跟 `_bridge_base.py` 同层 (跨 milestone 的共享代码)。
- 三个文件:
  - `schema.py` — 5 个 kind 的 row 校验 (per-kind required fields +
    extra_row_validator hook)
  - `unified_index.yaml` — 8 个 registry 一行 entry + kind / path /
    summary / produced_by / consumed_by / expected_mixes (仅
    bridge_env_registry)
  - `unified_index_loader.py` — load + validate + 三个 read-only
    inventory walk (licenses / hf_dataset / m0_to_downstream)
- 关键设计点 1: **schema 层不替代** module-local loader。`m1_rlvr/`
  / `m1_swe1/` 等的 prepare script 继续用 `_bridge_base.load_env_registry`
  做自己的校验。schema 层是 audit 工具，在 pytest 上层 cross-cut。
  Session 2 之后可以让两层 merge — 但现在先把 audit 工具落到位。
- 关键设计点 2: `KNOWN_BRIDGE_STATUSES` 在 schema.py 重复声明而不 import
  `_bridge_base`，保持 data_registries → bridge runtime 单向独立。然
  后用 pytest 验证两层是否对齐 — drift 由 test 发现，不靠 import 强
  绑定。
- 关键设计点 3: `bridge_env_registry` 的 `expected_mixes` 字段在
  unified_index.yaml 上声明，而不是在每个 registry 自己的 yaml 上。
  这样 schema 层就能 catch "RLVR 行错放到 SWE1 registry" 这种 copy-
  paste bug — 之前只在 bridge runtime 校验时才能发现。
- Live registries 全过 (`test_live_unified_index_validation_is_clean`
  return `[]`)。
- 19 个 pytest case 跨：schema 校验 6 + index shape 4 + live
  validation 2 + cross-registry inventory 4 + read-only 检查 1 + 双
  向对齐 1 + dispatcher 1。

测试基线 129 + 2 skipped → 148 + 2 skipped (19 new)。
`test_m1_agentic_sft.py` pyarrow collect-error pre-existing。

Roadmap §3 W1 row 状态从 "✗ — RL and eval data have no registry" → ⚠
(Session 1 ✓；eval registry 等 task019)。§5 critical-path #11 task030
加 Session 1 进展。

Session 2+ 不在本 PR:
- task019 / task020 落地后加 eval_basket_registry kind + index row
- Pre-commit / pre-PR hook 自动跑 `validate_unified_index()`
- 把 8 个 module-local loader 接进 schema 层 (merge 两层校验逻辑)
