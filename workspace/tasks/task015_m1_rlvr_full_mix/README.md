# task015_m1_rlvr_full_mix

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR #36 / f4ed9ae on 2026-05-18 -->

## 背景

`docs/implementation-roadmap.md` §1.3 / §5 critical-path 第 5 条:

> task015 — M1 RLVR full 21-env mix.

`stage1_rlvr/config/default.yaml::nemo_gym.config_paths` 加载 21 个 NeMo-Gym
env config。task014 Session 1 bridge 只覆盖了 4 个 (math_with_judge / code_gen
+ 两个 misnamed)，离 21 还差 17。这个 task 把整片登记 + 接入。

整 task 拆 Sessions：

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | Registry-driven mix derivation + RLVR1 name audit + RLVR2 接入 M0 已有的 envs | yes | ✓ Done (this PR) |
| 2+ | 等 task057 M0 expansion 一个一个 active 起来，自动被 bridge 拾起 | depends on task057 / task056 Session 2 / task016 | Todo |

## Session 1 目标

`src/nemotron/recipes/super3/milestones/m1_rlvr/rlvr_env_registry.yaml` —
全量声明 21 NeMo-Gym env：

- 每行字段：`nemo_gym_env`、`mix` (rlvr1/2/3)、`m0_env_id` (or null)、
  `status` (active / m0_missing / verifier_mismatch / blocked_external)、
  `m0_verifier`、`nemo_gym_verifier`、`license`、`notes`
- `mix` 分配：rlvr1 = foundations (math+code+single-step tool/search)，
  rlvr2 = instruction_following + structured + reasoning，
  rlvr3 = safety + advanced reasoning + tools

`prepare_m1_rlvr_jsonl.py` 改造：

- 加 `load_rlvr_env_registry()` / `derive_env_map()` / `coverage_report()` /
  `build_mix_profiles()`
- `MIX_PROFILES` / `RLVR{1,2,3}_ENV_MAP` 由 registry import-time 派生
- manifest 加 `coverage` 块 (counts + active/m0_missing/verifier_mismatch/
  blocked_external lists)
- `report.md` 加 Coverage section

**关键 correction**：task014 Session 1 的 RLVR1_ENV_MAP 用了两个不存在的 NeMo-Gym env 名字：
- `general_tool_calling` → 改 `single_step_tool_use_with_argument_comparison`
  (verifier 语义匹配：都比对 emitted tool-call args vs gold schema)
- `search_grounded_qa` → 从 active rlvr1 移除 (`default.yaml` 没有这个 server，
  HotpotQA single-hop shape 也不匹配 `search_pivot_...`)；登记成
  `m0_missing` 让 coverage report 看得到 gap

## Session 1 验收

- [x] `rlvr_env_registry.yaml` 21 NeMo-Gym env 全部声明
- [x] 每行 status 字段限定在 4 个已知值
- [x] `MIX_PROFILES` / RLVR{1,2,3}_ENV_MAP 由 registry 派生 (import-time)
- [x] RLVR1 audit + 2 个名字 correction
- [x] RLVR2 至少 2 个 active env (math_competition_numeric, structured_outputs_json)
- [x] manifest 含 `coverage` 块 (counts + per-status lists)
- [x] `report.md` 写出 Coverage section
- [x] 跑 rlvr3 (active=0) → raise coverage-aware error 而非 emit 空文件
- [x] 至少 18 个 pytest case
- [x] Roadmap §1.3 task015 + §5 critical-path Session 1 ✓

## 依赖

- 不依赖 cluster / W&B
- 依赖 task021 Session 2 落的 RLVR1_ARTIFACT / RLVR2_ARTIFACT / RLVR3_ARTIFACT 常量
- 后续 Session 拾起 task057 / task056 Session 2 / task016 添的 M0 envs

## Session 2+ 不在本 PR

整 task acceptance 是"≥ 8 envs live in single-node smoke + per-env reward
histograms in W&B"。这需要：

1. task057 把 m0_missing rlvr2/rlvr3 envs 加进 M0 (workplace_assistant /
   mcqa / instruction_following / calendar / reasoning_gym / ns_tools /
   search_pivot ...)
2. task056 Session 2 落 math_formal_lean (待 share-alike clearance)
3. task016 落 swe_pivot M0 数据对应 swerl_gen verifier shape
4. 集群上 NeMo-Gym 启 multichallenge / inverse_if / equivalence_llm_judge
   / jailbreak_detection / over_refusal_detection 的 judge model
   (blocked_external)
5. `stage1_rlvr/config/data_prep/{rlvr1,rlvr2,rlvr3}.yaml` 的 input_path
   从 `/lustre/...` 翻到 M0-derived artifact (这条其实是 task014 Session 2)

Bridge 这边不需要再改代码——只要 registry 翻状态，所有派生表自动 pickup。

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_rlvr/rlvr_env_registry.yaml` — 注册表
- `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py` — 桥接器
- `src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/default.yaml` — NeMo-Gym env 列表源头 (lines 327-352)
- `src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml` — M0 env / verifier 源头
- plan §5.3 + roadmap §1.3 / §5
