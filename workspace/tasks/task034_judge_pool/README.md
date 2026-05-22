# task034_judge_pool

M2 judge service pool scaffold for model versioning, calibration-set metadata,
and deterministic ensemble voting.

Session 1 is sandbox-only. It defines the local interface and mock behavior so
task029 safety rows and future task038 curriculum logic can depend on stable
judge-pool records without live model inference.

Out of scope for Session 1:
- task018 Session 3 live GenRM service deployment
- task018 Session 4 end-to-end RLHF
- live judge model hosting
- auth/secrets for judge services
- calibration corpora access
- reward service routing
- cluster inference
