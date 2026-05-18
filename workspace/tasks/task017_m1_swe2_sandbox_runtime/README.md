# task017_m1_swe2_sandbox_runtime

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #40 / e9adcba on 2026-05-18 -->
<!-- SESSION 4 LANDED: PR pending on 2026-05-18 -->

## 背景

`docs/implementation-roadmap.md` §1.5 / §5 critical-path 第 7 条：

> task017 — M1 SWE2 sandbox runtime.

`stage2_swe2/config/default.yaml` 用 OpenHands agent loop 跑 SWE-Bench
任务（agent_max_turns=200, concurrency=768）。container_formatter expects
SIF images per `instance_id`，三个 family：

- `swebench_sweb.eval.x86_64.{instance_id}.sif`
- `swegym_sweb.eval.x86_64.{instance_id}.sif`
- `r2egym_{instance_id}.sif`

整 task 拆 Sessions：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | SIF image mapping registry + SWE2 bridge skeleton (third bridge copy) | yes | ✓ Done (this PR) |
| 2 | OpenHands loop wrapper + M0 SWE2 trace converter + sandbox watchdog | partial (wrapper 单测 yes，真 Docker 起 no) | Todo |
| 3 | Cluster smoke launcher + Docker fallback for non-SLURM | no — 需 NemTron cluster + SIF images | Todo |
| 4 | `_bridge_base.py` 抽取 (RLVR + SWE1 + SWE2 + RLHF 同 pattern) | yes | ✓ Done (this PR) |

## Session 1 目标

镜像 task016 Session 1 模式但加 SIF 部分：

1. **SIF image mapping registry** (roadmap §1.5 第一条 acceptance):
   - `swe2_sif_registry.yaml` 声明 3 个 SIF family + filename_template +
     M0 candidate + license
   - `resolve_sif_path(instance_id, source, sif_dir)` → 完整 Path
   - `validate_sif_exists(path)` → bool（cluster 起 slot 前查文件在）
   - `instance_id` 必须 `[A-Za-z0-9_\-]+` (anti path-injection)
   - 拒未知 source；拒 filename_template 不含 `{instance_id}`

2. **SWE2 bridge skeleton** (parallel m1_rlvr / m1_swe1):
   - `swe2_env_registry.yaml`：单 NeMo-Gym env `swe_agents`，三行（一行
     per SIF source family），全 `m0_missing`
   - `prepare_m1_swe2_jsonl.py`：registry-driven 派生 `SWE2_PROFILE` /
     `SWE2_ENV_MAP`，今天 active=0 → coverage-aware error
   - tag_record 加 `nemo_gym_env: swe_agents` + `nemo_gym_mix: swe2` +
     `sif_source: <family>` (从 registry active 行查)
   - manifest `coverage` 块加 `sif_source_breakdown`（per-family status 计数）
   - lineage emit `SWE2_ARTIFACT` 指 M0 manifest

## Session 1 验收

- [x] 新模块 `m1_swe2/{__init__,prepare_m1_swe2_jsonl}.py` + `swe2_sif_registry.yaml` + `swe2_env_registry.yaml`
- [x] SIF registry 3 个 known sources；拒未知；拒 template 无 `{instance_id}`
- [x] `resolve_sif_path` 三 family 都过；拒路径注入 (`..` / `/` / `\\` / 空)
- [x] `validate_sif_exists` 真读 filesystem
- [x] SWE2 env registry 3 行 (一 per SIF family)，全 m0_missing；拒非-swe2 mix；拒未知 sif_source
- [x] `SWE2_PROFILE` / `SWE2_ENV_MAP` import-time 派生
- [x] `tag_record` 不动 M0 contract + 加 nemo_gym_env / mix / sif_source / row_index / split
- [x] Manifest `coverage` 含 `sif_source_breakdown` per-family
- [x] 今天 active=0 → `prepare()` raise coverage-aware error
- [x] End-to-end happy path 测试 (monkeypatch 注 active 行)
- [x] 至少 18 个 pytest case
- [x] Roadmap §1.5 + §5 critical-path Session 1 ✓ + Session 2-4 切片

## 依赖

- 不依赖 cluster / Docker / SIF images / W&B
- 依赖 task021 Session 2 落的 `SWE2_ARTIFACT` 常量
- Session 2 依赖 OpenHands 库 + SWE-Gym-Lite HF 下载
- Session 3 依赖 NemTron cluster + 真 SIF images
- Session 4 跟 task014 / task015 / task016 / task017 三个 bridge 模块同步抽 base

## Session 2+ 不在本 PR

Session 2 核心：OpenHands loop wrapper + M0 SWE2 trace converter +
sandbox watchdog/blocklist。M0 SWE2 trace 走 SWE-Gym-Lite agent
trajectory（多轮 agent rollout shape 跟 OpenHands 天然吻合），按 SIF
family `swegym` 登记。Sandbox watchdog 包含 memory_limit_mb / cpu_limit
/ network_policy / command_blocklist YAML 配置 + Python enforce 层
（subprocess 包一层）。

Session 3 是真 launch — 需要 NemTron cluster + SIF images 推到 lustre。
Docker fallback path 让本地 dev workstation 不用 SLURM 也能 smoke 单
instance。

Session 4 是 cleanup：RLVR + SWE1 + SWE2 三个 bridge module 80% 代码重
复，抽 `_bridge_base.py`。具体 API：`BridgeProfile` dataclass 拆出 mix
profile shape；`load_registry` / `derive_env_map` / `coverage_report`
泛型化（registry path + mix name 参数）；`prepare` 留 module-specific
hook（如 SWE2 的 sif_source tagging）。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_swe2/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/m1_swe1/prepare_m1_swe1_jsonl.py` — 模板（第二份 bridge copy）
- `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py` — 模板（第一份 bridge copy）
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe2/config/default.yaml` — NeMo-Gym 配置 + container_formatter 源头 (lines 14, 314, 333-336)
- plan §5.5 + roadmap §1.5 / §5
