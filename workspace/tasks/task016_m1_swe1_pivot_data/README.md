# task016_m1_swe1_pivot_data

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #38 / d04b694 on 2026-05-18 -->
<!-- SESSION 2 LANDED: PR pending on 2026-05-19 (M0 SWE-Gym-Lite → swe_pivot_tool_call converter; lights up SWE1 active row) -->

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
| 2 | M0 SWE pivot 数据 converter (SWE-Gym-Lite / R2E-Gym → single-step tool-comparison shape) | partial (sandbox 验 converter 单元；small HF streaming smoke 已跑通；全量扩量走集群) | ✓ Done sandbox part + review follow-up real-schema fix |
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

- 不依赖 cluster / W&B；small HF streaming smoke 已在 review follow-up 跑通
- 依赖 task021 Session 2 落的 `SWE1_ARTIFACT` 常量
- Session 2 依赖 SWE-Gym-Lite / R2E-Gym HF 下载 (license: apache-2.0 / 待确认)

## Session 2 目标 (sandbox part)

1. **新 M0 environment** `swe_pivot_tool_call`:
   - `environment_registry.yaml` 加 row (family software_engineering /
     verifier argument_match / max_turns 1 / sandbox none)
   - `prepare_m0_assets.SYSTEM_PROMPTS` 加 prompt

2. **新 M0 data row** `m0_swe_pivot_tool_call`:
   - `data_registry.yaml` 加 row 指 `SWE-Gym/SWE-Gym-Lite`
     (apache-2.0)，converter=`swe_gym_lite_pivot`
   - contamination_against [SWE-Bench Lite, SWE-Bench Verified]
   - hf_revision=`f70b1a29ab120eb0a0ee7a1deb029825e735b2b0`
   - SWE-Gym-Lite 只有 `train` split；val 在 smoke scale 从 train 顺序续取

3. **新 converter** `transform_swe_gym_lite_pivot`:
   - 有 trajectory 时抽取第一个 assistant tool call；public patch-only row
     则从 gold patch 第一个修改文件合成 `view_file` pivot
   - 输出 `expected_answer = {"name": ..., "arguments": <dict>}`
   - `responses_create_params.tools` = 固定 4 工具 schema
     (view_file / search / edit_file / run_tests)
   - `extra_env_info.pivot_type` ∈ {"exploration", "action"}：
     view/search/grep/ls/find_file 标 exploration，其他标 action
   - 错误路径：missing problem_statement / 无 messages 且无 patch fallback /
     no tool_calls / malformed JSON arguments → raise ValueError

4. **`swe1_env_registry.yaml` 翻面**：
   - `m0_missing` 那行改成 `m0_env_id: swe_pivot_tool_call, status: active`
   - 现在 swe1 mix 有 active env，bridge 不再 raise coverage error

5. **修 `test_m1_swe1_data_bridge.py` 两个 today-tests**:
   - `test_swe1_env_map_empty_today` → `test_swe1_env_map_lights_up_post_task016_session_2`
   - `test_prepare_raises_coverage_aware_error_today` → 加 monkeypatch
     把 _REGISTRY 切换到 all-inactive 状态，证明 error path 仍 working

6. **Tests** (`test_swe_gym_lite_pivot.py`, 21 cases):
   - Module surface 4
   - Happy path 5: 提取首个 tool call / pivot_type 分类 / tool schema
     在 responses_create_params / repo+instance_id metadata
   - First-tool-call selection 2: skip non-assistant / pick first when
     parallel calls
   - Arguments normalization 2: dict args / null args
   - Error surfaces 4: missing problem_statement / missing messages /
     no tool calls / malformed JSON
   - Registry integration 3: validate_registries / data_registry row /
     env_registry row

## Session 2 验收 (sandbox part)

- [x] 新 env `swe_pivot_tool_call` 在 environment_registry.yaml +
  SYSTEM_PROMPTS
- [x] 新 data row `m0_swe_pivot_tool_call` in data_registry.yaml 满
  足所有 schema/audit 约束 (contamination_against / license / hf_revision)
- [x] 新 converter `transform_swe_gym_lite_pivot` 注册进 CONVERTERS
- [x] SWE1_ENV_MAP = {"swe_pivot_tool_call": "swe_pivot_single_step_tool_use_with_argument_comparison"}
- [x] validate_registries 在 live main 跑 clean
- [x] 三个 audit (schema / revision-pins / contamination) 都 clean
- [x] 20 个原 PR pytest case + review follow-up 1 个 real-schema fallback case + 修 2 个 swe1 bridge today-tests
- [x] sandbox 测试基线 421 → 441 passed + 7 skipped

## Session 2 不在本 PR (cluster part)

- 全量 HF data prep 走 NemTron cluster 扩量
- SWE1 bridge 真跑出 SWE1 jsonl 接 cluster `nemotron super3 rl swe1`

## Session 3 不在本 PR

Cluster smoke launcher — 需要 NemTron cluster + NeMo-Gym
`single_step_tool_use_with_argument_comparison` server 起来。Pattern
跟 task014 Session 2 sandbox part 类似（registry + config + smoke yaml），
等接到 cluster 再开 PR。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_swe1/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py` — 模式来源 (task014 + task015)
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe1/config/default.yaml` — NeMo-Gym env 列表源头
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml` — M0 verifier 源头
- plan §5.4 + roadmap §1.4 / §5
