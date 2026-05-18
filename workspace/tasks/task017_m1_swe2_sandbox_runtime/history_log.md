# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 roadmap §5 critical-path 第 7 条派生。task017 整 task：SWE2 sandbox
runtime + OpenHands loop + 真 launcher。整块要 Docker / SLURM / SIF
images / OpenHands 库，大部分得集群，拆 4 个 Session。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 SWE2 bridge skeleton + SIF image mapping registry/resolver。设计：

- 新模块 `src/nemotron/recipes/super3/milestones/m1_swe2/`，跟 m1_rlvr /
  m1_swe1 并列。两份 YAML：
  - `swe2_sif_registry.yaml` 声明 3 个 SIF family (swebench / swegym /
    r2egym)，每行 filename_template + M0 candidate + license
  - `swe2_env_registry.yaml` 声明 NeMo-Gym agent `swe_agents`，三行
    (一 per SIF family)，全 m0_missing 今天
- SIF resolver:
  - `resolve_sif_path(instance_id, source, sif_dir)` → Path
  - `instance_id` 必须 `^[A-Za-z0-9_\-]+$`（SWE-Bench `<org>__<repo>-<n>`
    pattern；anti path-injection — `..`、`/`、`\` 都被拒）
  - `validate_sif_exists(path)` 真读 filesystem
  - 拒未知 source；拒 filename_template 不含 `{instance_id}`
- Bridge 镜像 m1_swe1 模式（第三份 copy，~80% 跟 RLVR + SWE1 重复）：
  - registry-driven `SWE2_PROFILE` / `SWE2_ENV_MAP` import-time 派生
  - `tag_record` 加 `nemo_gym_env: swe_agents` + `nemo_gym_mix: swe2`
    + `sif_source: <family>`（从 registry active 行查；SWE2-specific
    extension）
  - `coverage_report` 加 `sif_source_breakdown` per-family status 计数
    （SWE2-specific extension，让运维看出哪个 container family 还差
    M0 源）
  - 今天 active=0 → `prepare()` raise coverage-aware ValueError
- Code duplication 留给 Session 4：抽 `_bridge_base.py` 让 RLVR / SWE1
  / SWE2 共享 registry loader / derive_env_map / coverage_report 等。
  Session 1 不抽是因为：
  1. SWE2 加了 sif_source 字段，shape 还在变；过早抽象会被后续 Session
     2 的 watchdog 配置再撕一次
  2. Session 4 单做 refactor PR 评审更清晰
- 测试 `tests/recipes/super3/test_m1_swe2_data_bridge.py` 19 case：
  - SIF registry 加载 / 拒未知 source / 拒 template 无 `{instance_id}`
  - `resolve_sif_path` 三 family 各 1 + 拒未知 source + 拒路径注入 (.., /, 空)
  - `validate_sif_exists` 真读 filesystem
  - Env registry 加载 / 拒非-swe2 mix / 拒未知 sif_source
  - `derive_env_map` 过滤 active
  - `coverage_report` 含 `sif_source_breakdown`
  - SWE2_PROFILE / SWE2_ENV_MAP 形态
  - `tag_record` 保 M0 contract + 加 SWE2 tags
  - 今天 raise coverage-aware error
  - End-to-end happy path（monkeypatch active 行）→ JSONL + manifest +
    lineage tagged SWE2_ARTIFACT

测试基线 88 → 107 passed (M0 + lineage + chat + rlvr + swe1 + swe2 = 19 new).
`test_m1_agentic_sft.py` 在 sandbox 仍 pyarrow collect-error pre-existing.

Roadmap §1.5 task017 + §5 critical-path 加 Session 1 ✓ + Session 2/3/4 ☐ 切片。

Session 2+ 不在本 PR：OpenHands wrapper / Docker / cluster / bridge base
抽取都要其他依赖。这次只把数据/基础设施层 sandbox 部分铺好。

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #40 已 squash-merge 为 `e9adcba` 进 main — m1_swe2 模块 +
SIF registry/resolver + env registry + 第三份 bridge copy + 19 个 pytest
case 都进了 main。intern status 回 Idle (Session 28)。task017 整 task 仍
InProgress：Session 2 (OpenHands wrapper + SWE-Gym converter + sandbox
watchdog) / Session 3 (cluster smoke + Docker fallback) / Session 4
(`_bridge_base.py` 抽取) 没启动。下一个 critical-path 候选 (roadmap §5)：
task018 (M1 RLHF GenRM service)。

## Session 4 - 2026-05-18 - intern_nemontron_review_cc

实现 `_bridge_base.py` 抽取 — RLVR + SWE1 + SWE2 + RLHF 四个 bridge
module 共享 scaffolding。等到 4 个 module 都摆稳（每个加完 module-
specific extensions：SWE2 `sif_source` / RLHF `pref_dataset`）之后做这
个 refactor 才有意义；过早抽会被后续 module 撕。

抽到 `src/nemotron/recipes/super3/milestones/_bridge_base.py`:

- JSONL/JSON I/O helpers (read_jsonl / write_jsonl / write_json)
- `discover_m0_split_files(input_dir)` (4 个 module 用同一份代码读 M0)
- Status vocabulary (STATUS_ACTIVE / M0_MISSING / VERIFIER_MISMATCH /
  BLOCKED_EXTERNAL + `KNOWN_STATUSES` frozenset)
- `load_env_registry(path, expected_mix, ...)` — 通用 YAML loader：
  接受单值或集合 (SWE1/2/RLHF single mix；RLVR `{rlvr1, rlvr2, rlvr3}`)；
  `display_label` 让 module 自定错误措辞；`extra_row_validator` callback
  接 SWE2 `sif_source` 那种 module-specific 行检查
- `derive_env_map(registry, mix_name=None)` — 同时支持 single-mix (passes
  None) 和 multi-mix (RLVR 按 mix 过滤) 两种用法
- `base_coverage_report(registry, mix_name, filter_to_mix=False)` —
  通用 counts + per-status 列表
- `base_tag_record(record, ...)` — 通用 row tagger，`extra_row_fields` /
  `extra_metadata_fields` / `row_index_key` / `split_key` 让 module 加
  module-specific tag (SWE2 sif_source、RLHF pref_dataset、各自的
  swe1_/swe2_/rlvr_/rlhf_ row_index 前缀)
- `collect_mix_rows(files_by_env, env_map, split, max, tag_fn)` —
  通用 mix 切片 + 错误收集，`tag_fn` callback 让 module 提供 closure

留给 module:
- `MIX_NAME` / 注册表路径
- mix profile builder (3 mixes for RLVR vs 1 for others)
- `prepare()` 主流程（manifest 字段 + lineage outputs + 第二个 registry：
  SWE2 SIF、RLHF pref data）
- module-specific tag wrapping（SWE2 `sif_source` lookup、RLHF
  `pref_dataset` lookup）
- module-specific coverage extension（SWE2 `sif_source_breakdown`、
  RLHF `pref_dataset_breakdown` + `known_pref_candidates`）

行数对比：

| 文件 | Pre | Post | Δ |
|---|---|---|---|
| m1_rlvr/prepare_m1_rlvr_jsonl.py | 529 | 341 | -188 |
| m1_swe1/prepare_m1_swe1_jsonl.py | 451 | 312 | -139 |
| m1_swe2/prepare_m1_swe2_jsonl.py | 591 | 460 | -131 |
| m1_rlhf/prepare_m1_rlhf_jsonl.py | 550 | 401 | -149 |
| _bridge_base.py | n/a | 387 | +387 |
| **Total** | **2121** | **1901** | **-220** |

测试基线没变 — 129 passed + 2 skipped（task017 Session 1 / task013
Session 1 时候的同基线）。每个 module 测试文件没改一个字 — refactor 的
契约就是 "external behavior identical"。`test_m1_agentic_sft.py` pyarrow
collect-error pre-existing。

Roadmap §1.5 task017 Session 4 ☐ → ✓。task017 整 task 仍 InProgress：
Session 2 (OpenHands wrapper + SWE-Gym converter + watchdog) / Session
3 (cluster smoke + Docker fallback) 没启动 — 都需 cluster / Docker。

