# task133_benchmark_alignment_source_manifest_membership_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Add a top-level benchmark-alignment `source_manifests` allowlist for
  result-manifest files.
- Require every `evidence_records[*].source_manifests[*]` entry to be declared
  in that top-level allowlist.
- Preserve existing source-manifest path guards and raw artifact checks.

## Boundaries

- Static/offline validation only.
- No live benchmark/eval run, endpoint call, W&B, cluster job, data prep,
  training, artifact download, deployment, promotion, direct `main`/`master`
  push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task133_benchmark_alignment_source_manifest_membership_s1`
- Base: `36101b1e2152fd3f52cea8b0af5770c57d881227`
- PR: https://github.com/songCNMS/Nemotron/pull/240
