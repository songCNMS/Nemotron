# task182_runspec_docs_url_revision_pin_nano_super_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Pin mutable `tool.runspec.docs` URLs in Nano3 and Super3 recipe entrypoints
  from the repository `main` branch to exact Nemotron revision
  `510b6eec33edece3d212a3187b16db3d1b4a8a15`.
- Pin the matching examples/default docs URL in `docs/runspec/v1/spec.md`.
- Add focused static coverage that reads scoped files as text and does not
  import or execute recipe entrypoints.

## Boundaries

- Static metadata/docs/test/status only.
- No recipe execution, job submission, data prep, train/eval, endpoints, W&B,
  cluster, deploy, artifact operations, direct `main`/`master` push, or
  self-merge.

## Status

- Base: `df45842edade40c19fd0496f3844ef20653a94cc`
- Branch: `intern_nem_dev_1/task182_runspec_docs_url_revision_pin_nano_super_s1`
- PR: pending
- Head: pending validation and commit
- Checks: pending
