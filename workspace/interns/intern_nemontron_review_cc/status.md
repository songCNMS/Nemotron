# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task018_m1_rlhf_genrm_service -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task018_m1_rlhf_genrm_service |
| PR | pending push |
| Session | 29 |

正在做：task018 Session 1 — RLHF bridge skeleton + preference-data
candidate registry + KL invariant pytest。第四份 registry-driven bridge
copy（之前 RLVR + SWE1 + SWE2）。新模块 `m1_rlhf/` 含 `rlhf_env_registry.yaml`
两 NeMo-Gym envs (`genrm_compare` blocked_external + tool-call validity
m0_missing) + `rlhf_pref_data_registry.yaml` 三候选 (HelpSteer-2 /
UltraFeedback / Orca DPO pairs) + `prepare_m1_rlhf_jsonl.py` 加
`pref_dataset` tag + coverage 加 `pref_dataset_breakdown` +
`known_pref_candidates`。`test_rlhf_kl_invariants.py` 直接读 prod
default.yaml 严格断言 plan §5.6 三个 KL knob (penalty=1e-4, type=k3,
use_kl_in_reward=false) — sandbox 拦下 regression 不等 cluster 才发现。
今天 RLHF active=0 → coverage-aware error。18 个新 pytest case，sandbox
测试基线 107 → 125 passed。Session 2 (HelpSteer-2 converter) / Session 3
(GenRM judge deploy) / Session 4 (端到端 smoke) 都不在本 PR。
