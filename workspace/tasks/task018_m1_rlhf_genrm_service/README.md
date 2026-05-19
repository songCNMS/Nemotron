# task018_m1_rlhf_genrm_service

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #42 / e758604 on 2026-05-18 -->
<!-- SESSION 2 LANDED: PR pending on 2026-05-19 (M0 HelpSteer-2 → helpsteer2_pref_compare converter; genrm_compare stays blocked_external pending Session 3 judge service) -->

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
| 2 | M0 HelpSteer-2 (or UltraFeedback) converter — chosen/rejected pairs + tool-call pairing | partial (converter 单测 yes，真 HF 下载受限) | ✓ Done sandbox part (this PR); tool-call pairing harness deferred; 真 HF download 走集群 |
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

## Session 2 (sandbox part) — landed in this PR

1. **新 M0 env + data row** (`helpsteer2_pref_compare`)：
   - `environment_registry.yaml` 加 env: family `rlhf_preference` /
     verifier `genrm_compare` / max_turns 1 / sandbox none
   - `data_registry.yaml` 加 row 指 `nvidia/HelpSteer2` (cc-by-4.0,
     contamination_against [MT-Bench, HelpSteer1])
   - `prepare_m0_assets.SYSTEM_PROMPTS` 加 prompt

2. **新 converter** `transform_helpsteer2_pref`:
   - HelpSteer-2 两种 flavor 都支持:
     - **Explicit-pair**: `prompt` + `response_a/b` + `preference_label`
       ("A" / "B" / 大小写不敏感)
     - **Attribute-derived**: `prompt` + `response_a/b` + per-side
       rating attrs (`helpfulness_a/b`, `coherence_a/b`,
       `correctness_a/b`) → 聚合 (verbosity/complexity 故意不用) → label
   - Aliases 支持: `chosen`/`rejected` 当 `response_a`/`response_b`
   - **Explicit label 优先于 attribute-derived** (人工标注是 authoritative)
   - **One-sided missing attrs** → 有数据的一侧赢 (保 signal 不丢 row)
   - **Tie** → default "A" (stable ordering，operator 可通过
     `label_derivation` metadata post-filter)
   - 输出 shape per plan §5.6:
     - `responses_create_params.input` = [system, user(prompt)]
     - `extra_env_info.completion_a` / `completion_b`
     - `extra_env_info.preference_label` (+ `label_derivation`)
     - `expected_answer` = "A" / "B"
     - `reward_config.verifier` = `genrm_compare`

3. **RLHF pref-data registry 更新**:
   - `helpsteer2` 行加 `m0_landed: true` + `m0_data_row: m0_helpsteer2_pref`
   - notes 更新指明 Session 2 converter 已落

4. **RLHF env registry `genrm_compare` 状态不变**:
   - **故意保持 `blocked_external`**：判判服务部署 (task018 Session 3
     cluster ops) 仍是 blocker；只清了一个，row flip 到 active 要等两
     个都清
   - notes 更新指明 data-side blocker cleared，cluster-side blocker 仍在
   - 修一个 unified-registry 测试：`nvidia/HelpSteer2` 现在出现在两个
     registry (m0_data + pref_data)；测试改成断言 pref-candidate flag
     在 pref_data_registry entry 上即可

5. **Tool-call pairing harness 延后**：
   README 提到 "把 HelpSteer-2 prompts 跟 M0 hermes tool-call 数据
   cross-product 配对" 给 single_step_tool_use_with_argument_comparison
   那条 env 用。但那个 env 是 RLHF 的*平行 validity check*，不是
   GenRM 的 preference path；本 PR 聚焦 GenRM data；tool-call pairing
   harness 是独立工作 (需要先思考 cross-product 策略避免组合爆炸)，留到
   后续 session

6. **Tests** (`test_helpsteer2_pref.py`, 20 cases):
   - Module surface 2: SYSTEM_PROMPTS / CONVERTERS
   - Explicit-pair 4: A label / B label / lowercase / chosen+rejected aliases
   - Attribute-derived 5: A wins / B wins / tied → A / explicit overrides
     derived / one-sided missing
   - Error surfaces 4: missing prompt / missing response / invalid label /
     no labels nor attrs
   - Registry integration 3: validate_registries / data_registry row /
     env_registry row
   - RLHF registries 2: pref_data m0_landed / env_registry 保持
     blocked_external

## Session 2 验收 (sandbox part)

- [x] M0 env + data row 通过 schema / contamination / revision-pin audit
- [x] Converter explicit + derived 两路径都过；tie + missing 边界正常
- [x] `helpsteer2_pref_compare` 出现在 `validate_registries` 的环境校验里
- [x] RLHF pref_data registry 的 helpsteer2 row 现在带 `m0_landed: true`
- [x] RLHF env registry 的 `genrm_compare` 仍 `blocked_external` (Session
  3 judge service is the other blocker)
- [x] 20 个 pytest case；sandbox 测试基线 474 → 494 passed + 7 skipped

## Session 2+ 不在本 PR (cluster part + deferred bits)

- 真 HF download `nvidia/HelpSteer2` 走 NemTron cluster
- Revision pin (TBD → 真 commit hash)
- Tool-call pairing harness (HelpSteer-2 × hermes tool-call cross-product)
  — 留到 follow-up
- task018 Session 3：GenRM judge model server 部署 (cluster ops；
  起 Qwen3-Nemotron-235B-A22B-GenRM-2603 + router_dp_size=8 + TP=8)
- task018 Session 4：端到端 RLHF smoke 真跑

## (legacy comment) Session 2 核心：HelpSteer-2 converter。每行 M0 输出：
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
