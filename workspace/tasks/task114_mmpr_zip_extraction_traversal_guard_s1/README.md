# task114_mmpr_zip_extraction_traversal_guard_s1 - MMPR zip extraction traversal guard

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nem_dev_2,SESSION=15 -->

## Background

MMPR public, MMPR-Tiny, and the VLM preference prep stage extracted zip members
with `ZipFile.extract()` or `extractall()` directly. Archive member names that
are absolute paths, Windows drive paths, or contain `..` traversal could escape
the intended temporary extraction root before later layout checks ran.

## Goals

- Add a shared safe zip extraction helper for local data-prep archives.
- Reject absolute paths, drive-letter paths, `..` traversal, and resolved
  targets outside the extraction root.
- Use the helper in the public MMPR script, MMPR-Tiny script, and VLM
  preference prep stage.
- Preserve existing successful extraction layout, idempotency, and progress
  reporting.
- Add focused synthetic zip tests for normal extraction and traversal rejection.

## Out Of Scope

- Live Hugging Face downloads, large MMPR archive extraction, production data
  prep, training, eval, endpoint calls, W&B, cluster jobs, deployment, direct
  `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `d64cbd067a15cca222b9eba200af1eb1ec5b7788`.
- [x] Unsafe zip members are validated before extraction starts.
- [x] Public MMPR, MMPR-Tiny, and VLM preference prep use guarded extraction.
- [x] Synthetic tests prove traversal members are rejected without writing
  outside the intended extraction root.
- [x] Focused pytest, py_compile, Ruff, structured zip probe, and diff
  whitespace checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/222
