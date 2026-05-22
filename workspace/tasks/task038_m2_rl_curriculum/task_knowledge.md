# task038_m2_rl_curriculum - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

- Session 1 defines "env gap" as `max(0, target_reward - mean_reward)` plus an explicit coverage gap when a local rollout store has too few scored rollouts.
- `estimate_env_gaps` filters `LocalRolloutStore` traces by `model_version` and emits stable per-env gap records.
- `build_dynamic_sampling_plan` deterministically turns sampling weights into integer quotas using largest-remainder allocation.
- The sampler sorts envs by `env_id`, so results are stable even when callers pass estimates in a different order.
- `judge_response_to_rollout_metrics` is the local task034 bridge; it carries judge score, confidence, label, version key, and calibration id into rollout metrics without live judge calls.
- Closeout added no new implementation knowledge; PR #148 is merged and remaining RL curriculum work is cluster/live-service follow-up.
