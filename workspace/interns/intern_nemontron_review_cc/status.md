# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task017_m1_swe2_sandbox_runtime -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task017_m1_swe2_sandbox_runtime |
| PR | pending push |
| Session | 67 |

正在做：task017 Session 2 (sandbox part) — M0 SWE-Gym → SWE2 OpenHands
trace converter + sandbox watchdog policy。3 大件 (OpenHands wrapper 延后)：

1. **新 M0 env + data row** (`swe2_openhands_trace`)：verifier
   `openhands_loop`，sandbox=sif，max_turns=200；SWE-Gym/SWE-Gym-Lite
   来源 apache-2.0
2. **新 converter** `transform_swe_gym_openhands_trace`：保留**整个
   trajectory** (跟 task016 Session 2 first-tool-call 互补)；gold patch
   多源解析 (top-level / submit_patch 调用)；6-tool schema (含
   run_shell + submit_patch)
3. **SWE2 registry 翻面**：`swegym` 行 m0_missing → active；
   `SWE2_ENV_MAP = {"swe2_openhands_trace": "swe_agents"}`
4. **新 sandbox watchdog** `m1_swe2/sandbox_watchdog.py`：WatchdogPolicy
   dataclass + token-prefix command_blocklist + network_policy enum +
   subprocess enforcer；默认 policy YAML 阻止 rm -rf / / sudo / curl

33 个新 + 2 个修改 pytest case；sandbox 测试基线 441 → 474 passed +
7 skipped。三个 data-registry audit 全 clean。

**OpenHands wrapper 延后**理由：repo 没有跟 OpenHands 库的真集成
(只有 NeMo-Gym swe_agents service)；写没真 backing 的 wrapper 是接口
投机。等真 OpenHands 集成 PR (plan §10 cluster work) 落到再开 follow-up。

task017 整 task：Session 1 ✓ + Session 4 ✓ + Session 2 sandbox 部分 ✓
(converter + watchdog) + Session 2 OpenHands wrapper part 延后 +
Session 3 (cluster smoke + Docker fallback) 仍待。
