# task034_judge_pool - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

- Session 1 keeps judge-pool behavior sandbox-only and deterministic.
- `JudgeModelVersion.version_key` is the reproducibility key carried through each `JudgeResponse` and `EnsembleVoteResult`.
- `CalibrationSet` records env-scoped calibration metadata and validates sample count plus score range/stddev before use.
- `MockJudge` can score from per-request overrides or a stable SHA-256 hash path for local tests.
- `evaluate_ensemble` sorts responses by frozen judge version key before aggregating, so voting is deterministic independent of input judge order.
- `DeferredLiveJudgeAdapter` is an explicit boundary for future live GenRM/judge service routing; it intentionally raises until production dependencies are ready.
- Session 2 added no new judge-pool implementation knowledge; it confirmed PR #145 merge and handed off the local judge-pool contract for task038 sandbox curriculum work.
