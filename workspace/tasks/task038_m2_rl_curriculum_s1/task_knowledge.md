# task038_m2_rl_curriculum_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

- The landed task038 implementation lives in `workspace/tasks/task038_m2_rl_curriculum/` and `src/nemotron/recipes/super3/milestones/m2_rl_curriculum/`.
- Session 1 defines "env gap" as target reward minus mean reward, with coverage gap support for under-covered local rollout traces.
- The dynamic sampler uses deterministic largest-remainder quota allocation over per-env weights.
- The local judge bridge carries task034 `JudgeResponse` score, confidence, label, version key, and calibration id into rollout metrics without live judge calls.
- Closeout added no new implementation knowledge; remaining task038 work is cluster/live-service follow-up.
