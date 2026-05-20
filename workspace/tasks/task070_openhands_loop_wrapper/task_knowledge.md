# task070 - task_knowledge

## Why a wrapper rather than direct integration

The OpenHands library has its own opinions about agent state, action
schema, and observation handling. The Nemotron wrapper exists to:

1. **Adapt the action schema** — OpenHands ships with a richer action
   space than the task017 6-tool schema (view_file / search / edit_file
   / run_shell / run_tests / submit_patch). The wrapper translates
   OpenHands actions to/from the Nemotron tool calls so downstream
   verification (argument_match) stays consistent.
2. **Inject the watchdog** — OpenHands runs shell commands directly via
   its own subprocess module; the wrapper intercepts those so
   `sandbox_watchdog.enforce_subprocess` gets the policy decision.
3. **Bound the rollout** — OpenHands' built-in turn budget doesn't know
   about the per-instance timeout (`swebench_agent_timeout`) — wrapper
   layers both bounds.
4. **Normalize telemetry** — the rollout store (task032, M2) expects a
   uniform per-turn dict shape across SWE harnesses (SWE1 first-tool-
   call, SWE2 OpenHands rollout, future OpenCode / Codex). Wrapper
   emits the uniform shape regardless of upstream library.

## Decision: Protocol vs ABC

Use `typing.Protocol` (not an ABC) so the wrapper interface is
structural — a fake stub doesn't need to inherit from anything; type
checker is happy. ABC would force ceremony for tests.

## Decision: Failure modes return reward 0, not raise

Plan §10 risks table mentions "sandbox instability — training
interruptions and noisy rewards". The wrapper's contract is: a single
broken instance produces reward 0, but the rollout returns. Raising
would crater the batch. The terminal_reason field surfaces *why* reward
is 0 (container_crash / tool_schema_mismatch / timeout /
policy_violation) so the dashboard can break it down.

## Real OpenHands integration target

OpenHands ships `openhands` PyPI package (or its successor; check
current naming during Session 2). The wrapper imports `OpenHandsLoop`
or equivalent from there for `OpenHandsLoopAdapter`. The SIF container
ships a Python env with the package preinstalled (task021 Session 3
sandbox containers had this implicitly; verify during Session 2).

## Not in this task

- Real OpenHands library install — that's part of the SIF container
  build (task021 Session 3+)
- OpenCode / Codex equivalents — M2 task026 (SWE multi-harness)
- Per-harness reward calibration — M2 task034 (judge pool) or task038
  (M2 RL curriculum)
