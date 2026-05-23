# task038_m2_rl_curriculum_s3 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

- S3 adds `EnvJudgeRoutingPolicy`, `JudgeDispatchRecord`, `rollout_trace_to_judge_request`, `judge_ensemble_result_to_rollout_metrics`, and `dispatch_judge_ensembles_for_rollouts` under `m2_rl_curriculum`.
- The dispatcher is sandbox-only: it builds mock judges from task034 `JudgeVersionRegistry` refs and calls `evaluate_ensemble`; it does not call live GenRM, reward services, cluster inference, training, or W&B/lineage.
- Dispatch metrics use `judge_score` and `judge_confidence`, so existing S1 `estimate_env_gaps` consumes aggregate judge output through the established rollout metrics path.
