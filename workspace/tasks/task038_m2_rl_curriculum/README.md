# task038_m2_rl_curriculum

M2 RL curriculum scaffold for per-environment gap estimation and deterministic
dynamic sampling.

Sessions 1-3 are sandbox-only. Session 1 reads synthetic/local
`LocalRolloutStore` traces, estimates per-env reward gaps, and allocates
sampling quota toward failing or under-covered environments. Session 2 adds
per-env/per-checkpoint reward calibration summaries. Session 3 adds a local
judge ensemble dispatcher that routes env-specific mock judge refs through the
landed task034 judge-pool contract.

Out of scope for these sandbox sessions:
- task014 real RLVR cluster smoke
- task021 launch path / scheduler integration
- task034 Session 2+ live judge model/service deployment
- task040 numeric pass-rate production signal beyond synthetic traces
- cluster smoke/full M2 RL run
- W&B/lineage publication
- production rollout store backend
- live reward calibration
- live GenRM/judge service deployment
- reward-service routing
- auth/secrets and calibration corpora access
