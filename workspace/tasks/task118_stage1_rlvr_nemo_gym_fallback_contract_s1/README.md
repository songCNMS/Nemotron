# task118_stage1_rlvr_nemo_gym_fallback_contract_s1 - Stage1 RLVR NeMo-Gym fallback contract

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nem_dev_2,SESSION=16 -->

## Background

`stage1_rlvr/train.py` had a local `ImportError` fallback for the NeMo-Gym
datum converter. The fallback constructed an empty `DatumSpec` with no user
payload and `stop_strings=None`, masking missing NeMo-Gym support and bypassing
the Qwen stop-string contract.

## Goals

- Align Stage1 RLVR with sibling Stage2 RL train scripts by failing fast when
  the NeMo-Gym converter import is unavailable.
- Ensure the local empty-message, `stop_strings=None` fallback cannot return.
- Add focused tests for missing converter behavior and converter delegation.
- Keep scope limited to Stage1 RLVR train loading, tests, and bookkeeping.

## Out Of Scope

- Live RL training, NeMo-Gym launch, endpoint calls, W&B, cluster jobs,
  deployment, promotion, direct `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `40eab704f6d02dd65e94189f098e712be6a1f6f2`.
- [x] Stage1 RLVR imports the NeMo-Gym converter directly and fails loudly if
  the converter is unavailable.
- [x] Tests prove missing converter raises and converter delegation preserves
  the payload supplied by the converter.
- [x] RLVR smoke shard, focused pytest, py_compile, Ruff, static fallback probe,
  and diff whitespace checks pass.
- [ ] PR opened to `main`.

## PR

- Pending branch push.
