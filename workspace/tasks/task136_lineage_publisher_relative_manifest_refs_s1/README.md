# task136_lineage_publisher_relative_manifest_refs_s1 - Lineage publisher relative manifest refs

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

Task135 aligned `validate_chain()` with `walk_chain()` for relative
`LineageInput(kind="manifest")` refs. The publishing helper still passed raw
relative manifest refs to the default upstream resolver, so
`maybe_publish_lineage_from_manifest()` could leave valid relative upstreams
unresolved depending on the process working directory.

## Goals

- Resolve relative manifest upstream refs against the declaring manifest
  directory when publishing from `maybe_publish_lineage_from_manifest()`.
- Preserve absolute manifest refs, checkpoint heuristic refs, HF/unknown
  unresolved behavior, dry-run behavior, and failure tolerance.
- Preserve custom `upstream_artifact_resolver` override semantics and pass the
  original `LineageInput` to custom resolvers.
- Keep the public lineage JSON/dataclass contract unchanged.

## Acceptance Criteria

- [x] Branch starts from `main`
  `691d50dfdad536409b2879638bc811355d6b7b20`.
- [x] Dry-run publishing resolves a relative upstream manifest to
  `<upstream_artifact_name>:latest`.
- [x] Fake live W&B publishing calls `use_artifact()` for a relative upstream
  manifest.
- [x] Custom resolver receives the original relative `LineageInput.ref`.
- [x] Broken relative manifest refs remain unresolved and do not crash.
- [x] Focused pytest, py_compile, Ruff, structured probe, and diff checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/243
