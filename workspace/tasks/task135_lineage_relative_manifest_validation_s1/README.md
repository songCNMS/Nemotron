# task135_lineage_relative_manifest_validation_s1 - Lineage relative manifest validation

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

`walk_chain()` resolves `LineageInput(kind="manifest")` relative paths against
the manifest that declares the input. `validate_chain()` walked the same chain
but validated `inp.ref` relative to the current working directory, which made
valid self-contained relative lineage manifests fail validation.

## Goals

- Make `validate_chain()` resolve manifest inputs the same way `walk_chain()`
  does.
- Preserve absolute manifest ref support.
- Preserve clean single-record root manifests.
- Keep missing upstream refs visible with clear declaring-stage diagnostics.

## Acceptance Criteria

- [x] Branch starts from `main`
  `36101b1e2152fd3f52cea8b0af5770c57d881227`.
- [x] Clean M0 <- M1 relative manifest refs walk and validate cleanly.
- [x] Broken relative manifest refs still produce an operator-facing issue.
- [x] Existing absolute-ref behavior stays covered.
- [x] Focused lineage pytest, py_compile, Ruff, structured probe, and diff
  checks pass.
- [ ] PR opened to `main`.

## PR

- Pending
