# history_log

<!-- METADATA:SESSION=2 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 roadmap §5 critical-path 第 8 条派生。task018 整 task：RLHF 数据 bridge
+ pref data + GenRM judge service + 端到端 smoke。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 RLHF bridge skeleton + preference-data candidate registry + KL
invariant pytest。设计：

- 新模块 `src/nemotron/recipes/super3/milestones/m1_rlhf/`：第四份
  registry-driven bridge copy（之前 RLVR + SWE1 + SWE2）。
- 两份 YAML：
  - `rlhf_env_registry.yaml` 两行 (NeMo-Gym envs)：
    - `genrm_compare` (`blocked_external`：需 pref data + GenRM judge model
      deployment)
    - `single_step_tool_use_with_argument_comparison` (`m0_missing`：需
      pref+tool-call pairing harness)
  - `rlhf_pref_data_registry.yaml` 3 候选：HelpSteer-2 (cc-by-4.0, primary)
    / UltraFeedback (mit, secondary) / distilabel-orca-pairs (apache-2.0,
    backup)
- Bridge `prepare_m1_rlhf_jsonl.py` 跟 SWE2 模板对照：
  - registry-driven `RLHF_PROFILE` / `RLHF_ENV_MAP` import-time 派生
  - `tag_record` 加 `pref_dataset: <id>` 字段（从 active row 查；SWE2
    类比就是 `sif_source`）
  - `coverage_report` 加 `pref_dataset_breakdown` + `known_pref_candidates`
    两个 RLHF-specific 字段
- KL invariant pytest (`test_rlhf_kl_invariants.py`) 读 prod default.yaml
  递归找 3 个 key，严格断言：
  - `reference_policy_kl_penalty == 1.0e-4`
  - `reference_policy_kl_type == "k3"`
  - `use_kl_in_reward is False`
  这是 plan §5.6 acceptance 的硬指标，任何 PR 改一个值都在 sandbox 就 fail，
  不等 cluster run 才发现。
- `_find_scalar` 用 sentinel `_MISSING` 区分"没找到"vs "找到了 False/None"。
  之前一版用 `default=None` 会把 `use_kl_in_reward=False` 当成"没找到"，
  改用 sentinel 防 false negative。
- Code duplication 留给 task017 Session 4 (`_bridge_base.py` 抽取)：现在
  是第四份 copy，shape 还在加 module-specific extension (SWE2 的
  sif_source、RLHF 的 pref_dataset)，过早抽会被撕。

测试 18 case 跨两个文件：
- `test_m1_rlhf_data_bridge.py` 15 case
- `test_rlhf_kl_invariants.py` 3 case (KL trio)

测试基线 107 → 125 passed (M0 + lineage + chat + rlvr + swe1 + swe2 +
rlhf + KL invariants). `test_m1_agentic_sft.py` 在 sandbox 仍 pyarrow
collect-error pre-existing.

Roadmap §1.6 task018 + §5 critical-path 加 Session 1 ✓ + Session 2-4 ☐ 切片。

Session 2+ 不在本 PR：
- Session 2 (HelpSteer-2 M0 converter) — 需 HF 下载 + 法务 review
- Session 3 (GenRM judge model 部署) — 需 cluster + GPUs
- Session 4 (端到端 smoke from SWE2 checkpoint) — 需上述都到位

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #42 已 squash-merge 为 `e758604` 进 main — m1_rlhf 模块 +
env registry + pref data candidate registry + 4th bridge copy + KL
invariant pytest + 18 个 pytest case 都进了 main。intern status 回 Idle
(Session 30)。task018 整 task 仍 InProgress：Session 2 (HelpSteer-2
converter) / Session 3 (GenRM judge deploy) / Session 4 (端到端 smoke)
没启动。

里程碑：roadmap §5 critical-path 前 8 条（task005/012/021/014/015/016/017/018）
全部 Session 1 落地 ✓。下一个候选：task013 (M1 two-stage SFT loss，
critical-path 唯一没动的) / task019-020 (M1 eval basket) / task017 Session 4
(`_bridge_base.py` 抽取，4 个 bridge module 都摆稳) / 之前 task 的 Session
2+。
