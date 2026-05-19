# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 68 |

刚做完：task017 Session 2 sandbox part — SWE2 OpenHands trace converter
+ sandbox watchdog policy (PR #82 / 959d8e1, merged 2026-05-19)。3 大件:

1. **新 M0 env + data row** (`swe2_openhands_trace`)：verifier
   `openhands_loop`，sandbox=sif，max_turns=200；SWE-Gym/SWE-Gym-Lite
   sibling 跟 task016 SWE1 row (同 HF source 不同 converter)
2. **新 converter** `transform_swe_gym_openhands_trace`：保留**整个
   trajectory** (跟 SWE1 first-tool-call 互补)；gold patch 多源解析；
   6-tool schema (含 run_shell + submit_patch)
3. **SWE2 registry 翻面**：`swegym` 行 m0_missing → active；
   `SWE2_ENV_MAP` 不再空
4. **新 sandbox watchdog** `m1_swe2/sandbox_watchdog.py`：WatchdogPolicy
   dataclass + token-prefix command_blocklist + network_policy enum +
   subprocess enforcer；默认 policy 阻止 rm -rf / / sudo / curl / 外
   网

33 个新 + 2 个修改 pytest case；sandbox 测试基线 441 → 474 passed + 7
skipped。三个 data-registry audit 全 clean。

**OpenHands wrapper 延后**：repo 没有跟 OpenHands 库的真集成；写没真
backing 的 wrapper 是接口投机。等真 OpenHands 集成 PR (plan §10
cluster work) 落到再开 follow-up。

**M1 converter layer (sandbox) 全部落地**:
- task014 Session 1+2 sandbox ✓ (RLVR1 bridge + smoke wiring)
- task015 Session 1 ✓ (21-env registry)
- task016 Session 1+2 sandbox ✓ (SWE1 bridge + SWE-Gym pivot converter)
- task017 Session 1+2+4 sandbox ✓ (SWE2 bridge + trace converter +
  watchdog + _bridge_base)
- task018 Session 1 ✓ (RLHF bridge skeleton) — Session 2 仍待

下一候选 (sandbox-runnable):
- **task018 Session 2** — HelpSteer-2 / UltraFeedback converter unit tests
  (M1 converter layer 最后一块 sandbox)
- task017 OpenHands wrapper follow-up — 等真 library 集成才有意义
- 之前 task 的 Session 2+ — 大都需 cluster
