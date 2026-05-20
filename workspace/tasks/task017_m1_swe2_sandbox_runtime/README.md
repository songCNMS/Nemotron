# task017_m1_swe2_sandbox_runtime

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #40 / e9adcba on 2026-05-18 -->
<!-- SESSION 4 LANDED: PR #46 / 5943e18 on 2026-05-18 -->
<!-- SESSION 2 LANDED: PR pending on 2026-05-19 (M0 SWE-Gym → swe2_openhands_trace converter + sandbox watchdog policy; OpenHands wrapper deferred) -->

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
| 2 | OpenHands loop wrapper + M0 SWE2 trace converter + sandbox watchdog | partial (wrapper 单测 yes，真 Docker 起 no) | ⚠ Sandbox part (converter + watchdog) ✓ (this PR); OpenHands wrapper deferred to follow-up session |
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
- Session 2 依赖 OpenHands 库；small SWE-Gym-Lite HF streaming smoke 已在 review follow-up 跑通
- Session 3 依赖 NemTron cluster + 真 SIF images
- Session 4 跟 task014 / task015 / task016 / task017 三个 bridge 模块同步抽 base

## Session 2 (sandbox part) — landed in this PR

1. **新 M0 env + data row** (`swe2_openhands_trace`):
   - `environment_registry.yaml` 加 env: family software_engineering /
     verifier `openhands_loop` (binary patch+tests) / max_turns 200 /
     sandbox sif (训练时由 OpenHands gym 在 SIF container 里 enforce)
   - `data_registry.yaml` 加 row 指 `SWE-Gym/SWE-Gym-Lite` (apache-2.0,
     contamination_against [SWE-Bench Lite, SWE-Bench Verified])
   - hf_revision=`f70b1a29ab120eb0a0ee7a1deb029825e735b2b0`；SWE-Gym-Lite
     只有 `train` split，val 在 smoke scale 从 train 顺序续取
   - `prepare_m0_assets.SYSTEM_PROMPTS` 加对应 prompt

2. **新 converter** `transform_swe_gym_openhands_trace`:
   - 跟 task016 Session 2 (SWE1 first-tool-call) **互补**：本 converter
     保留**整个 trajectory**，因为 SWE2 verifier 奖励 full rollout 的
     patch+tests 结果不是单步决策
   - 6-tool schema：view_file / search / edit_file / **run_shell** /
     run_tests / **submit_patch** (比 SWE1 4-tool 更丰富，agent 要能
     真正运行 + 提交 patch)
   - Gold patch 解析：top-level `patch` / `gold_patch` → fallback 扫
     trajectory 找 `submit_patch` 调用 → 都没有 raise ValueError
   - `extra_env_info.reference_trajectory` 携带 normalize 后的整段
     messages (tool_calls arguments 全 decode 成 dict)；public patch-only
     row 则合成 read-then-submit minimal trajectory
   - `extra_env_info.sif_source` 默认 `swegym`，可被 row-level 字段
     覆盖 (R2E-Gym 等 mixed-family 场景)

3. **SWE2 registry 翻面**：`swegym` 行 status `m0_missing` → `active`，
   `m0_env_id: swe2_openhands_trace`；`SWE2_ENV_MAP = {"swe2_openhands_trace":
   "swe_agents"}`；bridge 不再 raise coverage error

4. **新 sandbox watchdog** (`m1_swe2/sandbox_watchdog.py`):
   - `WatchdogPolicy` frozen dataclass: command_blocklist / network_policy
     (deny / allow_internal / allow) / cpu_limit / memory_limit_mb / notes
   - `load_watchdog_policy(path)` YAML loader + validator
   - `is_command_blocked(policy, argv)` **token-level prefix match** —
     `rm -rf /` 不会假阳性匹配 `rm -rf /workspace/build`
   - `enforce_subprocess(policy, argv, **kw)` 包 subprocess.run，
     blocked argv 抛 `SandboxPolicyViolation`
   - Default policy YAML `sandbox_watchdog_default.yaml`:
     network=deny / cpu=4 / mem=8GB / blocklist 含 rm -rf / sudo /
     curl / wget / apt install 等

5. **修 2 个 SWE2 bridge today-tests** (parallel task016 Session 2 pattern)

6. **Tests** (33 new + 2 modified)：
   - `test_swe2_openhands_trace.py` 16: module surface 3 / happy path 6 /
     patch fallback 1 / error surfaces 3 / registry integration 3 /
     SWE2_ENV_MAP lights up
   - `test_sandbox_watchdog.py` 15: dataclass surface 2 / load 6 /
     is_command_blocked 5 / enforce_subprocess 2 / default policy 1
   - `test_m1_swe2_data_bridge.py` 2 today-tests flipped

## Session 2 验收 (sandbox part)

- [x] M0 env + data row 通过 schema / contamination / revision-pin
  audit
- [x] Converter 全 trajectory 保留 + 6-tool schema + patch 多源解析
- [x] SWE2_ENV_MAP 不再空；coverage 报告 swegym=active
- [x] Watchdog policy load + token-prefix match + subprocess enforce
- [x] 33 个新 + 2 个修改 pytest case；sandbox 测试基线 441 → 474 passed
  + 7 skipped

## OpenHands wrapper 延后 → lifted to task070 (2026-05-19; renamed from task067 due to ID collision)

README Session 2 originally listed OpenHands wrapper + converter +
watchdog 三件事。task017 Session 2 (PR #82) 落了后两件 (converter +
watchdog)。

OpenHands wrapper deferral 理由：repo 没有跟 OpenHands 库的真集成
(只有 stage2_swe2/config 引用 NeMo-Gym swe_agents service)；写一个没
真 backing 的 wrapper 是接口投机。

**Now tracked**: `workspace/tasks/task070_openhands_loop_wrapper/` —
Session 1 (Protocol + FakeOpenHandsLoop stub + watchdog wiring + per-
turn telemetry) is sandbox-runnable and is the natural follow-on pick.
Sessions 2-3 cluster-bound.

## Session 2+ 不在本 PR (cluster part)

- 全量 HF data prep 走 NemTron cluster 扩量
- OpenHands wrapper (真集成等 plan §10 cluster work)
- 真 SIF container 起 → OpenHands rollout → patch+tests 验证

Session 3 是真 launch — 需要 NemTron cluster + SIF images 推到 lustre。
Docker fallback path 让本地 dev workstation 不用 SLURM 也能 smoke 单
instance。

Session 4 已落地 (PR #46 / 5943e18) — `_bridge_base.py` 把 RLVR / SWE1
/ SWE2 / RLHF 四个 bridge 80% 重复代码抽出来 (load_env_registry /
derive_env_map / coverage_report / collect_mix_rows / discover_m0_split_files
/ tag_record helpers)。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_swe2/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/m1_swe1/prepare_m1_swe1_jsonl.py` — 模板（第二份 bridge copy）
- `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py` — 模板（第一份 bridge copy）
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe2/config/default.yaml` — NeMo-Gym 配置 + container_formatter 源头 (lines 14, 314, 333-336)
- plan §5.5 + roadmap §1.5 / §5
