# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task018_m1_rlhf_genrm_service -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task018_m1_rlhf_genrm_service |
| PR | pending push |
| Session | 69 |

正在做：task018 Session 2 (sandbox part) — M0 HelpSteer-2 → genrm_compare
converter。3 大件:

1. **新 M0 env + data row** (`helpsteer2_pref_compare`)：family
   `rlhf_preference`，verifier `genrm_compare`；`nvidia/HelpSteer2`
   (cc-by-4.0, contamination_against [MT-Bench, HelpSteer1])

2. **新 converter** `transform_helpsteer2_pref`：handle 两种 HelpSteer-2
   flavor (explicit-pair + attribute-derived)；`chosen`/`rejected`
   aliases；tie → "A"；explicit label > derived

3. **RLHF registries 更新**：
   - pref_data registry helpsteer2 行加 `m0_landed: true` flag
   - env_registry `genrm_compare` 状态**故意保持** `blocked_external`：
     judge service (task018 Session 3) 仍是 blocker；row flip 到 active
     要等两个都清

20 个新 pytest case + 1 修 (unified registry inventory)；sandbox 测试
基线 474 → 494 passed + 7 skipped。三个 data-registry audit 全 clean。

**Tool-call pairing harness 延后**：README Session 2 提的 HelpSteer-2 ×
hermes tool-call cross-product 给 single_step_tool_use_with_argument_comparison
那条 env 用，但是独立工作 (需思考组合爆炸策略)；留 follow-up session。

**M1 converter layer (sandbox) 全部落地** (本 session 完成最后一块):
- task014 (RLVR1 bridge + smoke wiring) ✓
- task015 (21-env registry) ✓
- task016 (SWE1 bridge + SWE-Gym pivot converter) ✓
- task017 (SWE2 bridge + OpenHands trace converter + sandbox watchdog) ✓
- task018 (RLHF bridge + HelpSteer-2 converter) ✓

剩下 task018 Session 3/4 (judge service + 真 smoke) 都需 cluster。
