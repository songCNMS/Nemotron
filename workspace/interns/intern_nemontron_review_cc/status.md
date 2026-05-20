# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task070_openhands_loop_wrapper -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task070_openhands_loop_wrapper |
| PR | pending push |
| Session | 77 |

正在做：task070 Session 1 — OpenHands loop wrapper Protocol + fake stub
+ watchdog wiring + per-turn telemetry。Lifted from task017 Session 2
deferral (after task067 ID-collision rename).

## What's in this PR

### 新 module `m1_swe2/openhands_loop.py`

- **Dataclasses**:
  - `Instance` (frozen): instance_id / repo / problem_statement /
    sif_path / agent_max_turns (default 200) / timeout_s (default 3600)
  - `TurnRecord` (frozen): turn_index / tool_name / argument_dict /
    observation_length_chars / latency_ms / blocked_by_watchdog
  - `RolloutResult` (frozen): instance_id / reward (binary 0.0|1.0) /
    terminal_reason (validated against `VALID_TERMINAL_REASONS`) /
    turn_count / submitted_patch / elapsed_s / turns tuple

- **Terminal reasons enum** (8 + unknown):
  solved / patch_rejected / tests_failed / turn_budget / timeout /
  policy_violation / container_crash / tool_schema_mismatch /
  unknown

- **`OpenHandsLoop` Protocol** — structural, no ABC inheritance needed
- **`FakeOpenHandsLoop`** deterministic stub:
  - Canned trajectory + canned terminal reason + canned reward
  - Routes `run_shell` / `run_tests` through
    `sandbox_watchdog.is_command_blocked`
  - `view_file` / `search` / `edit_file` NOT gated (sandboxed Python
    runtime, not fresh shell)
  - Bounded by `agent_max_turns` + `timeout_s` (injected clock for
    testability)
  - Blocked command → terminal=`policy_violation` + reward 0; the turn
    record marks `blocked_by_watchdog=True`
- **`aggregate_turn_telemetry`** rolls up per-turn records into task021
  Session 1 aggregate contract shape (numeric → min/mean/max, counts →
  int, tool_name_counts → dict)

### Tests (`test_openhands_loop.py`, 16 cases)

- Dataclass surface 4: terminal reasons enum / reward must be binary /
  unknown terminal raises / valid binary outcomes accepted
- Protocol satisfaction 1
- Happy path 2: reward 1 + terminal=solved / per-turn telemetry captured
- Bounded rollout 2: turn budget exceeded / clock timeout exceeded
- Watchdog integration 3: blocked shell → terminal=policy_violation +
  blocked_by_watchdog=True / safe shell commands pass / view/search/
  edit_file NOT gated
- Failure modes 1: container_crash flows through
- aggregate_turn_telemetry 3: empty turns / tool_name + violation
  counting / shape matches task021 contract

Sandbox 测试基线 543 → **559 passed + 7 skipped** (16 new)。

## task070 状态

- Session 1 ✓ (this PR) — Protocol + FakeOpenHandsLoop + watchdog +
  telemetry
- Session 2 ☐ — Real `OpenHandsLoopAdapter` against upstream OpenHands
  library (depends on library availability in SIF container)
- Session 3 ☐ — Cluster smoke (`nemotron super3 rl swe2 -c smoke`
  against 1 SWE-Bench Verified instance with the adapter)

Roadmap §5b sandbox queue 更新：task070 Session 1 ✓；Session 2 partial。
