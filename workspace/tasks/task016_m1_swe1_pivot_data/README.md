# task016_m1_swe1_pivot_data

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

`docs/implementation-roadmap.md` §1.4 / §5 critical-path 第 6 条：

> task016 — M1 SWE1 pivot data.

`stage2_swe1/config/default.yaml::nemo_gym.config_paths` 只加载一个 NeMo-Gym
env config: `swe_pivot_single_step_tool_use_with_argument_comparison`。
Verifier 是 `argument_match` 家族（比对 emitted 首个 tool call 的 name +
args 跟 gold pivot 调用）。

数据 `input_path` 同 task014 / task015，指向 NVIDIA 内部 `/lustre/...`
placeholder — M0 → SWE1 没接起来。

整 task 拆 Sessions：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | SWE1 bridge skeleton: 新模块 `m1_swe1/` + registry-driven `prepare_m1_swe1_jsonl.py`，今天 active=0 → coverage-aware error path | yes | ✓ Done (this PR) |
| 2 | M0 SWE pivot 数据 converter (SWE-Gym-Lite / R2E-Gym → single-step tool-comparison shape) | partial (sandbox 验 converter 单元；真 HF download 要联网) | Todo |
| 3 | Cluster smoke launcher | no — 等 NemTron cluster | Todo |

## Session 1 目标

镜像 task015 Session 1 的 registry-driven bridge 模式，**但 SWE1 只有一个
NeMo-Gym env**：

- 新模块 `src/nemotron/recipes/super3/milestones/m1_swe1/{__init__,prepare_m1_swe1_jsonl}.py` + `swe1_env_registry.yaml`
- Registry 起步两行：
  1. `nemo_gym_env: swe_pivot_..., m0_env_id: null, status: m0_missing` —
     Session 2 把这行翻成 active
  2. `nemo_gym_env: swe_pivot_..., m0_env_id: swe_pivot_patch_supervision, status: verifier_mismatch` —
     M0 现有 SWE-bench Lite 源是 `patch_diff_match`，跟 NeMo-Gym 的
     `argument_match` 不匹配，登记说清楚
- Bridge 逻辑跟 m1_rlvr 几乎一样（~80% 重复，task017 SWE2 落第三版时再
  做 `_bridge_base.py` 抽取）
- `tag_record` 给行加 `nemo_gym_env: swe_pivot_..._argument_comparison` + `nemo_gym_mix: swe1`
- manifest 加 `coverage` 块；lineage emit `SWE1_ARTIFACT` 指 M0 manifest
- 今天 active=0 → `prepare()` raise coverage-aware ValueError (列出 gap)

## Session 1 验收

- [x] 新模块 `m1_swe1/{__init__,prepare_m1_swe1_jsonl}.py` + `swe1_env_registry.yaml`
- [x] Registry 两行，status 限定 4 个已知值
- [x] `load_swe1_env_registry()` 拒绝 mix != "swe1" 的行
- [x] `derive_env_map()` / `coverage_report()` / `build_mix_profile()` 函数
- [x] `SWE1_PROFILE` / `SWE1_ENV_MAP` import-time 由 registry 派生
- [x] Manifest 含 `coverage` 块 + `lineage` 块 (artifact_type = SWE1_ARTIFACT)
- [x] 跑 SWE1 (active=0) → raise coverage-aware error 而非 emit 空文件
- [x] End-to-end happy path 测试（monkeypatch 注入 synthetic active row）
- [x] 至少 13 个 pytest case
- [x] Roadmap §1.4 + §5 critical-path Session 1 ✓

## 依赖

- 不依赖 cluster / W&B / HF
- 依赖 task021 Session 2 落的 `SWE1_ARTIFACT` 常量
- Session 2 依赖 SWE-Gym-Lite / R2E-Gym HF 下载 (license: apache-2.0 / 待确认)

## Session 2+ 不在本 PR

Session 2 要做的核心：从 SWE-Gym-Lite 或 R2E-Gym 提取 single-step tool-call
pivot 数据。每行 M0 输出：

- `responses_create_params.input`: SWE issue 的 problem statement
- `responses_create_params.tools`: 通用工具 schema (view_file, search,
  edit_file, run_tests, ...)
- `expected_answer` / `extra_env_info`: gold 首个 tool call (name + args)
- `reward_config.verifier`: `argument_match`

关键判断：从 SWE-Gym agent trajectory 里抽 **第一个真实有效的 tool call**
当 ground truth；那些只 view-or-search 的纯探索行为也要标。设计需要先看
SWE-Gym 数据 shape，再决定具体抽取逻辑。

Session 3 是真集群 launch — 需要 NemTron cluster + NeMo-Gym
`single_step_tool_use_with_argument_comparison` server 起来。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_swe1/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py` — 模式来源 (task014 + task015)
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe1/config/default.yaml` — NeMo-Gym env 列表源头
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml` — M0 verifier 源头
- plan §5.4 + roadmap §1.4 / §5
