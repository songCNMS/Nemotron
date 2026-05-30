# Task Knowledge

<!-- METADATA:SESSION=1 -->

- The M2 release packet should be treated as an approval artifact, not as an
  execution artifact. The generated command scripts dry-run first and keep
  live smoke commands held until resources exist and PM explicitly releases
  execution.
- All 8 M2 targets need a frozen Qwen3.5-122B-A10B baseline artifact set before
  candidate-vs-baseline comparison: `baseline_manifest.json`, `metrics.json`,
  `raw_results/`, `config.yaml`, and `artifact_sha256_manifest.txt`.
- Common acceptance criteria across targets: env/path variables defined on the
  approved run host without secret values in logs, accepted asset/database
  roots present with checksum or size manifests, one-sample dry-run writes a
  config dump, one-sample live smoke only after fresh PM release, and slashless
  `/v1/chat/completions` plus Qwen chat template kwargs where supported.
- Highest-risk resource gaps are exact Tool Decathlon asset identity,
  MCPMark service fleet provisioning, BIRD real-execution database bundle, and
  BrowseComp/HLE judge or search credential policy.
