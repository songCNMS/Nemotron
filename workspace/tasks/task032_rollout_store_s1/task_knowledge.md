# task032_rollout_store_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

- PR #135 landed `LocalRolloutStore`, `RolloutKey`, and `RolloutTrace` for repo-local JSONL/indexed rollout storage keyed on `(prompt_id, model_version, env_id)`.
- Production backend, W&B/lineage stream integration, cluster deployment, and retention policy enforcement remain separate infra follow-ups.
