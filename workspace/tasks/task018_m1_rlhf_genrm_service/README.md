# task018_m1_rlhf_genrm_service

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

`docs/implementation-roadmap.md` §1.6 / §5 critical-path 第 8 条：

> task018 — M1 RLHF GenRM service.

`stage3_rlhf/config/default.yaml::nemo_gym.config_paths` 加载两个 NeMo-Gym
env：

- `genrm_compare` — GenRM 偏好判官 (uses `nvidia/Qwen3-Nemotron-235B-A22B-GenRM-2603`，
  router_dp_size=8, TP=8)
- `single_step_tool_use_with_argument_comparison` — 平行 tool-call 有效性
  检查 per plan §5.6

KL 配置 (lines 98-100)：`reference_policy_kl_penalty=1e-4`、
`reference_policy_kl_type="k3"`、`use_kl_in_reward=false`。这是 plan §5.6
acceptance 的硬指标，要有 pytest gate 防 regression。

整 task 拆 Sessions：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | RLHF bridge skeleton + pref-data candidate registry + KL invariant pytest | yes | ✓ Done (this PR) |
| 2 | M0 HelpSteer-2 (or UltraFeedback) converter — chosen/rejected pairs + tool-call pairing | partial (converter 单测 yes，真 HF 下载受限) | Todo |
| 3 | GenRM judge model 部署 (cluster ops — Qwen3-Nemotron-235B-A22B-GenRM-2603 起 inference 服务) | no — 需 cluster + GPUs | Todo |
| 4 | 端到端 RLHF smoke run from SWE2 checkpoint，验 KL penalty + tool-call validity | no — 需 cluster + judge service + SWE2 checkpoint | Todo |

## Session 1 目标

镜像 task017 Session 1 模式：4th registry-driven bridge copy + 数据候选
registry + plan-conformance pytest。

1. **RLHF bridge skeleton**：
   - 新模块 `m1_rlhf/__init__.py` + `prepare_m1_rlhf_jsonl.py`
   - `rlhf_env_registry.yaml` 两行：`genrm_compare` (`blocked_external` — 需
     pref data + judge service)、`single_step_tool_use_with_argument_comparison`
     (`m0_missing` — 需 pref+tool-call pairing harness)
   - `RLHF_PROFILE` / `RLHF_ENV_MAP` import-time 派生
   - `tag_record` 加 `pref_dataset: <id>` 字段（从 active row 查）
   - `coverage_report` 加 RLHF-specific 字段：
     - `pref_dataset_breakdown`：per-pref-candidate status histogram
     - `known_pref_candidates`：pref data 候选 registry id list

2. **Preference data candidate registry**：
   - `rlhf_pref_data_registry.yaml` 3 个候选：
     - `helpsteer2` (nvidia/HelpSteer2, cc-by-4.0) — 默认 primary
     - `ultrafeedback` (openbmb/UltraFeedback, mit) — secondary blend
     - `distilabel_orca_pairs` (argilla/distilabel-intel-orca-dpo-pairs,
       apache-2.0) — backup
   - 每行字段：`id`, `hf_dataset`, `hf_revision_pin_required`, `license`,
     `pref_pair_field` (是否需推导 vs 直 column), `contamination`,
     `notes`
   - `pref_candidate_ids(registry)` helper

3. **KL invariant pytest** (`test_rlhf_kl_invariants.py`)：
   - 读 `stage3_rlhf/config/default.yaml`，递归找 KL 三个 key
   - 严格断言：`penalty == 1.0e-4`、`type == "k3"`、`use_kl_in_reward is False`
   - 任何一个被改了，PR 在 sandbox 就 fail；cluster run 之前先发现

## Session 1 验收

- [x] 新模块 `m1_rlhf/{__init__,prepare_m1_rlhf_jsonl}.py` + `rlhf_env_registry.yaml` + `rlhf_pref_data_registry.yaml`
- [x] Env registry 2 行（genrm_compare blocked_external + tool-call m0_missing）；拒非-rlhf mix；拒未知 status
- [x] Pref data registry 3 候选；拒缺字段
- [x] `RLHF_PROFILE` / `RLHF_ENV_MAP` import-time 派生
- [x] `coverage_report` 含 `pref_dataset_breakdown` + `known_pref_candidates`
- [x] `tag_record` 加 `pref_dataset` 字段
- [x] 今天 active=0 → `prepare()` raise coverage-aware error
- [x] End-to-end happy path 测试（monkeypatch active 行）→ JSONL + manifest + lineage tagged RLHF_ARTIFACT
- [x] KL invariant pytest 3 个断言全过
- [x] 至少 18 个 pytest case
- [x] Roadmap §1.6 + §5 critical-path Session 1 ✓ + Session 2-4 切片

## 依赖

- 不依赖 cluster / W&B / HF / Docker
- 依赖 task021 Session 2 落的 `RLHF_ARTIFACT` 常量
- Session 2 依赖 HelpSteer-2 HF 下载 + 法务 review (cc-by-4.0 注意 attribution)
- Session 3 依赖 cluster + judge model checkpoint
- Session 4 依赖 task017 Session 2+ 落 SWE2 checkpoint

## Session 2+ 不在本 PR

Session 2 核心：HelpSteer-2 converter。每行 M0 输出：
- `responses_create_params.input`: pref prompt
- `extra_env_info.completion_a` / `completion_b`: 两个候选完成
- `expected_answer` / `preference_label`: A or B (从 helpfulness +
  coherence aggregate 推导)
- `reward_config.verifier`: `genrm_compare`

Tool-call pairing harness：把 HelpSteer-2 prompts 跟 M0 hermes tool-call
数据 cross-product 配对，让 plan §5.6 那条"tool-call 在 RLHF 阶段
还有效"的检查能跑。

Session 3 / 4 是真集群 — 不在 sandbox 范围。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_rlhf/` — 本 task Session 1 产物
- `src/nemotron/recipes/super3/milestones/m1_swe2/prepare_m1_swe2_jsonl.py` — 模板（第三份 bridge copy）
- `src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml` — NeMo-Gym 配置源头（KL 三个 key + GenRM 模型 + judge 配置）
- plan §5.6 + roadmap §1.6 / §5
