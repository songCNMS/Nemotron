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

