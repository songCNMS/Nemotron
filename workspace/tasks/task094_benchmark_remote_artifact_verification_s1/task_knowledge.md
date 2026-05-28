# task094_benchmark_remote_artifact_verification_s1 knowledge

<!-- METADATA:SESSION=10 -->

## Working Notes

- Benchmark alignment uses `validate_raw_artifact_paths()` from
  `qwen_eval_repro_gate.py`; `vm4vpn:` and `vpn:` refs are remote refs detected
  by `is_remote_artifact_reference()`.
- Generic artifact-check statuses still include `local_workspace_verified`, but
  remote benchmark raw artifacts must be stricter: only `pm_verified` is valid.
- Task094 normalized metadata only. It did not run live artifact probes,
  endpoints, W&B, cluster jobs, deployment, or benchmark execution.
- Session 10 added no new task094-specific implementation knowledge; task097
  owns the RLHF tool-call contamination skip-contract follow-up.
