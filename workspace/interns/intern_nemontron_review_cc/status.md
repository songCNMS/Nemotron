# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle,TASK= -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | |
| PR | N/A |
| Session | 30 |

最近：task018 Session 1 (PR #42 `e758604`) 已 squash-merge 进 main —
第四份 registry-driven bridge copy (RLVR / SWE1 / SWE2 之后)，新模块
`m1_rlhf/` 含 `rlhf_env_registry.yaml` (genrm_compare blocked_external
+ tool-call validity m0_missing) + `rlhf_pref_data_registry.yaml`
(HelpSteer-2 / UltraFeedback / Orca DPO 三候选) + `prepare_m1_rlhf_jsonl.py`
(加 `pref_dataset` tag + coverage `pref_dataset_breakdown` +
`known_pref_candidates`)。`test_rlhf_kl_invariants.py` 严格断言 plan §5.6
KL trio (penalty=1e-4, type=k3, use_kl_in_reward=false) — sandbox-time
regression gate。18 个新 pytest case，sandbox 测试基线 107 → 125 passed。

task018 整 task 仍 InProgress：Session 2 (HelpSteer-2 converter) /
Session 3 (GenRM judge deploy) / Session 4 (端到端 smoke from SWE2
checkpoint) 待开。

下一个候选：roadmap §5 critical-path 前 8 条全部 Session 1 落地 ✓。
现在 critical-path 收尾候选：
- **task013** (M1 two-stage SFT loss — 唯一没动的 critical-path; sample-level loss + GRPO bridge)
- **task019** / **task020** (M1 eval basket — 等 task014 Session 2 拿到 RLVR checkpoint 才有用)
- **task021 Session 3-4** (sandbox containers + cluster verify — 部分要 cluster)
- **task017 Session 4** (`_bridge_base.py` 抽取 — 现在 4 个 bridge module 都摆稳)
- **task014/015/016/017/018 Session 2+** — 大都要 cluster 或 HF 下载
