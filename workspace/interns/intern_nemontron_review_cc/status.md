# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 78 |

刚做完：task070 Session 1 — OpenHands loop wrapper Protocol + fake stub
+ watchdog wiring + per-turn telemetry (PR #101 / f1a704a, merged
2026-05-19).

- 新 module `m1_swe2/openhands_loop.py`：
  - `Instance` / `TurnRecord` / `RolloutResult` frozen dataclasses
    (RolloutResult invariants: binary reward 0|1, validated terminal_reason)
  - 9-value terminal_reason enum (solved / patch_rejected /
    tests_failed / turn_budget / timeout / policy_violation /
    container_crash / tool_schema_mismatch / unknown)
  - `OpenHandsLoop` Protocol (structural, no ABC)
  - `FakeOpenHandsLoop` deterministic stub: canned trajectory + canned
    terminal_reason + canned reward; routes run_shell / run_tests
    through sandbox_watchdog; injectable clock for timeout testing
  - `aggregate_turn_telemetry()` rolls into task021 Session 1 contract
- 16 个新 pytest case; sandbox 测试基线 543 → 559 passed + 7 skipped

## 本轮 PRs 收尾 (Roadmap refresh → 5 new sandbox sessions in 24h)

- PR #94 — roadmap refresh + 4 gap-task scaffolds (task040 / task067 /
  task068 / task069)
- PR #95 — task067 → task070 rename (ID collision)
- PR #97 — task013 Session 2a (two-stage SFT driver + YAMLs)
- PR #99 — task040 Session 1 (W1 curriculum sampler)
- PR #101 — task070 Session 1 (OpenHands wrapper Protocol + fake)

Sandbox 测试基线 progression: 506 → 520 → 543 → 559 passed + 7 skipped
(任 3 个 sandbox sessions 共 53 个新测试).

## task070 状态

- Session 1 ✓ (this PR)
- Session 2 ☐ — Real `OpenHandsLoopAdapter` against upstream OpenHands
  library; depends on library availability in SIF container
- Session 3 ☐ — Cluster smoke

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 1 — M0 tier2 expansion (lights up RLVR2/RLVR3 active)
- task068 Session 1 — RLHF tool-call pairing harness design doc
- task069 Session 1 — W&B lineage publisher (injectable W&B run +
  FakeWandbRun + scripts/publish_lineage.py CLI)

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster part / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task070 Sessions 2-3。
