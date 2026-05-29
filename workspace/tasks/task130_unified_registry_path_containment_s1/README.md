# task130_unified_registry_path_containment_s1 - Unified registry path containment

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

The unified data registry loader resolved each index row path relative to
`unified_index.yaml`, but accepted absolute paths and traversal outside the
intended registry root. Validation could therefore report an out-of-root
registry as clean, and inventory walks could read escaped registry files.

## Goals

- Harden unified registry path resolution for validation and inventory walks.
- Reuse the same guarded path loader in sibling audit modules that consume
  unified-index `entry["path"]`.
- Reject absolute paths, empty or dot path components, traversal outside the
  registry root, symlink escapes, missing files, and directories.
- Preserve the shipped `data_registries/unified_index.yaml` sibling-registry
  layout.
- Add focused offline tests for clean and rejected path cases.

## Acceptance Criteria

- [x] Branch starts from `main`
  `df587d239f573503347f7e36f5f8354ff581a186`.
- [x] `validate_unified_index()` uses guarded registry path resolution.
- [x] `licenses_inventory()`, `hf_dataset_inventory()`, and
  `m0_to_downstream_inventory()` use the same guarded resolution.
- [x] Contamination, license, revision, and eval-overlap audit paths use the
  same guarded loader.
- [x] Focused tests cover clean relative paths, traversal, absolute paths,
  symlink escapes, missing files, directories, and malformed path components.
- [x] Audit-only CLI regression proves escaped registry paths are rejected
  before a malicious row can be reported.
- [x] Production unified index validation stays clean.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/239
