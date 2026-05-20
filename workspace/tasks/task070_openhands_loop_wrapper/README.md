# task070_openhands_loop_wrapper

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->
<!-- SESSION 1 LANDED: PR pending on 2026-05-19 (Protocol + FakeOpenHandsLoop + watchdog wiring + per-turn telemetry; 16 tests) -->

## 背景

Lifted out of `task017_m1_swe2_sandbox_runtime` Session 2.

task017 Session 2 originally bundled three deliverables: M0 SWE2 trace
converter (✓ landed), sandbox watchdog policy (✓ landed), and OpenHands
loop wrapper (deferred). The wrapper was deferred because at the time the
repo had no real integration with the OpenHands library — only references
to a NeMo-Gym-side `swe_agents` service in `stage2_swe2/config/default.yaml`.
Writing a wrapper without a real integration target would have been
interface speculation likely to need rework once the cluster integration
PR lands.

This task is the formal owner of that work, so the deferral has a tracked
home instead of being a footnote in task017's README.

## 范围

Build a thin Nemotron-side wrapper over the OpenHands agent loop that
the SWE2 stage drives during rollout. The wrapper sits between
`stage2_rl/stage2_swe2/train.py` (or its NeMo-Gym agent shim) and the
upstream OpenHands library, adding Nemotron-specific concerns:

- **Sandbox container handle** — wrapper owns the SIF / Docker / Podman
  container lifecycle (start, mount, tear down). Uses
  `runtime_shim.ContainerSandbox` from task021 Session 5.
- **Sandbox watchdog policy enforcement** — every shell command the agent
  emits is run through `m1_swe2/sandbox_watchdog.enforce_subprocess`
  (task017 Session 2 ✓).
- **Per-turn telemetry** — emit per-turn tool_name / argument_dict /
  observation_length / latency to the task021 telemetry stream so the
  rollout store (M2 task032) has a uniform shape across SWE harnesses.
- **Bounded rollout** — respect `agent_max_turns` (default 200 from
  stage2_swe2 config) and `swebench_agent_timeout` (default 3600s).
- **Failure modes** — capture container crash / tool schema mismatch /
  timeout as terminal-but-non-fatal outcomes; emit reward=0 instead of
  raising so the rollout doesn't crater the policy gradient batch.

## 整 task 拆 Sessions

| Session | 子条目 | sandbox-runnable? | Status |
|---|---|---|---|
| 1 | Interface contract + fake-OpenHands stub for unit tests — `OpenHandsLoop` protocol + `FakeOpenHandsLoop` implementing it deterministically; sandbox watchdog + telemetry wiring tested against the fake | yes | ✓ Done (this PR) |
| 2 | Real OpenHands library integration — `OpenHandsLoopAdapter` implementing the protocol against the upstream library; depends on the OpenHands python package being available in the SIF container | partial (interface yes, real run no) | Todo |
| 3 | Cluster smoke: `nemotron super3 rl swe2 -c smoke` runs 1 SWE-Bench Verified instance end-to-end with the wrapper | no — needs NemTron cluster + SIF image + checkpoint | Todo |

## Session 1 目标

1. **Interface** — `src/nemotron/recipes/super3/milestones/m1_swe2/openhands_loop.py`:
   - `OpenHandsLoop` Protocol with `start(instance)`, `step(observation)`,
     `submit_patch(patch)`, `close()` methods + `RolloutResult` dataclass
   - `FakeOpenHandsLoop` deterministic implementation for testing
     (canned trajectory; configurable terminal outcome)
2. **Watchdog integration** — wrapper enforces every shell command
   through `sandbox_watchdog.enforce_subprocess`; blocked command →
   recorded as failure-mode "policy_violation" with reward 0
3. **Telemetry** — per-turn dict matching task021 Session 1 telemetry
   schema (with new fields `tool_name`, `argument_dict`,
   `observation_length_chars`, `latency_ms`); aggregate
   `rollout_turns`, `final_outcome`, `terminal_reason`
4. **Tests** (≥ 15): protocol method coverage, watchdog blocked-command
   path, bounded turn count, timeout boundary, terminal outcome
   classification, reward-0-on-failure semantics

## Session 1 验收

- [x] `m1_swe2/openhands_loop.py` 新模块: `Instance` / `TurnRecord` /
  `RolloutResult` frozen dataclasses + `OpenHandsLoop` Protocol +
  `FakeOpenHandsLoop` test stub + `aggregate_turn_telemetry` helper +
  `VALID_TERMINAL_REASONS` enum (8 reasons + unknown)
- [x] Wrapper threads watchdog policy through `run_shell` / `run_tests`
  (view_file / search / edit_file 不过 shell — locked in dedicated test)
- [x] Per-turn telemetry shape matches task021 Session 1 contract
  (latency_ms + tool_name + argument_dict + observation_length_chars)
- [x] Bounded rollout: turn budget exceeded → terminal=turn_budget;
  timeout exceeded → terminal=timeout (tested with injected clock)
- [x] Failure modes produce reward 0 + terminal_reason, never raise
  (container_crash path validated; policy_violation path validated)
- [x] **16 个 pytest case** (vs ≥ 15 acceptance)
- [x] aggregate_turn_telemetry rolls up per-turn records into task021
  shape (numeric → min/mean/max, counts → int, tool_name_counts → dict)

Sandbox 测试基线 543 → 559 passed + 7 skipped (16 new)。

## 依赖

- task017 Session 2 (sandbox watchdog ✓) — already landed
- task021 Session 1 (telemetry schema ✓) — already landed
- task021 Session 5 (ContainerSandbox runtime shim ✓) — already landed
- Session 2 依赖 OpenHands library 真集成 (cluster work)
- Session 3 依赖 NemTron cluster + SIF image + SWE2 checkpoint

## 参考文件

- `src/nemotron/recipes/super3/milestones/m1_swe2/sandbox_watchdog.py` — policy enforcement layer
- `src/nemotron/recipes/super3/milestones/m1_swe2/prepare_m1_swe2_jsonl.py` — bridge that produces the training data the wrapper consumes
- `src/nemotron/recipes/super3/milestones/sandbox_containers/runtime_shim.py` — container lifecycle
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe2/config/default.yaml` — SWE2 stage config (agent_max_turns + container_formatter)
- plan §5.5 + §10 + roadmap §1.5
