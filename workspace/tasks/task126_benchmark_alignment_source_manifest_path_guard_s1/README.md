# task126_benchmark_alignment_source_manifest_path_guard_s1 - Benchmark alignment source manifest path guard

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

`benchmark_alignment.py` validates benchmark-improvement evidence
`source_manifests` separately from the Qwen eval repro gate. Its
repo-relative path helper rejected absolute and missing files but did not
reject traversal components, empty or dot components, symlink escapes, or
directories.

## Goals

- Harden benchmark alignment `source_manifests` validation with normal
  repo-relative components.
- Resolve candidate paths with `strict=True` and require containment under
  `REPO_ROOT`.
- Reject directories and symlink escapes.
- Add focused tests in a new benchmark-alignment path-guard shard without
  touching Qwen eval repro gate files.

## Acceptance Criteria

- [x] Branch starts from `main`
  `7d49d91a5cc2c49e17d617690d63d8a92ecb696b`.
- [x] Production benchmark alignment ledger source manifests validate.
- [x] Normal repo-relative files are accepted.
- [x] Traversal, empty/dot components, symlink escapes, and directories are
  rejected.
- [x] `validate_benchmark_alignment_ledger()` surfaces bad evidence
  `source_manifests`.
- [x] Focused pytest, py_compile, Ruff, structured path probe, and diff
  whitespace checks pass.
- [ ] PR opened to `main`.

## PR

- Pending.
