# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 66 |

刚做完：task016 Session 2 sandbox part — M0 SWE-Gym-Lite → SWE pivot
tool-call converter (PR #80 / 7c3c717, merged 2026-05-19)。3 大件：

1. **新 M0 env + data row** (`swe_pivot_tool_call`)：verifier
   `argument_match`，SWE-Gym/SWE-Gym-Lite 来源，apache-2.0
2. **新 converter** `transform_swe_gym_lite_pivot`：抽 trajectory 第一
   个 assistant tool call 当 ground truth；`extra_env_info.pivot_type` ∈
   {exploration, action}；纯 exploration pivot 仍 emit 但 tag
3. **SWE1 registry 翻面**：`m0_missing` → `active`，`SWE1_ENV_MAP`
   = `{"swe_pivot_tool_call": "swe_pivot_single_step_..."}`；
   bridge 不再 raise coverage error

20 个新 pytest case + 修 2 个 swe1 bridge today-tests；sandbox 测试
基线 421 → 441 passed + 7 skipped。三个 data-registry audit 全 clean。

task016 整 task：Session 1 ✓ + Session 2 sandbox 部分 ✓；真 HF
download + revision pin + cluster smoke (Session 3) 仍待。

**M1 converter layer 进展**:
- task014 Session 1+2 sandbox ✓ (RLVR1 bridge + smoke wiring)
- task015 Session 1 ✓ (21-env registry)
- task016 Session 1+2 sandbox ✓ (SWE1 bridge + SWE-Gym pivot converter)
- task017 Session 1 ✓ (SWE2 bridge skeleton) — Session 2 待
- task018 Session 1 ✓ (RLHF bridge skeleton) — Session 2 待

下一候选 (sandbox-runnable):
- **task017 Session 2** — OpenHands loop wrapper + SWE2 trace converter
  (wrapper unit tests；真 Docker run skipped)
- **task018 Session 2** — HelpSteer-2 / UltraFeedback converter unit tests
- 之前 task 的 Session 2+ — 大都需 cluster
