# task109_qwen_eval_local_raw_artifact_fingerprint_s1 knowledge

<!-- METADATA:SESSION=14 -->

## Working Notes

- Local raw artifact SHA256s are recorded per evidence record under
  `raw_artifact_sha256`, keyed by the exact local path string from
  `raw_artifact_paths`.
- Remote `vm4vpn:` and `vpn:` paths are excluded from fingerprint validation
  and continue to require `remote_artifact_check.status == "pm_verified"`.
- The current local MMLU calibration artifact fingerprints are:
  `930ee46c8c31944cada6065a5251a329f0bdf31d4b33d51c0cdc45222a97777b` for the
  summary JSON, and
  `2d575c8a613c76833c74f7bf20372fb243352ff1d24db24f11aa5a411de0d085` for the
  result JSONL.
