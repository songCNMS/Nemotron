# task038_m2_rl_curriculum - History Log

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-22

- Synced clean `main` to `f0695b7d9421ca1f6667044ed5c8c8f71fce44e0` before implementation.
- Started branch `intern_nem_dev_2/task038_m2_rl_curriculum_s1`.
- Implemented sandbox per-environment gap estimation over synthetic/local `LocalRolloutStore` traces.
- Added deterministic dynamic sampling quota allocation from gap weights.
- Added a local judge-pool metrics bridge that converts `JudgeResponse` into rollout metrics without live judge service calls.
- Rebased cleanly after `origin/main` advanced to `010e657df7648132bf485ffa0753d0e5d64fe802`.
- Opened PR #148 to `main` from branch `intern_nem_dev_2/task038_m2_rl_curriculum_s1`.
- Follow-up explicitly deferred: task014 real RLVR cluster smoke, task021 launch path/scheduler integration, task034 live judge deployment, production rollout store backend, W&B/lineage publication, reward service routing, and full cluster M2 RL runs.

## Session 2 - 2026-05-23

- Synced clean `main` to `5b940c90267f543d8fe5c8bd78ec2e119258b6a4` before implementation.
- Started branch `intern_nem_dev_2/task038_m2_rl_curriculum_s2`.
- Rebased cleanly after `origin/main` advanced to `37f314418b952e3007bb80ec21283aff5e83ce12`.
- Added sandbox per-environment, per-checkpoint reward calibration summaries over synthetic/local `LocalRolloutStore` traces.
- Added deterministic z-score and min/max normalized reward outputs with stable missing and zero-variance handling.
- Preserved Session 1 gap-estimator and dynamic-sampler behavior.
- Verified focused S2/S1/rollout/judge shard: 29 passed, `py_compile` passed, and `git diff --check` passed.
- Opened PR #157 to `main` from branch `intern_nem_dev_2/task038_m2_rl_curriculum_s2`.
- Follow-up remains cluster RL/training launch, live judge deployment, production rollout backend, W&B/lineage publication, and live reward calibration.
