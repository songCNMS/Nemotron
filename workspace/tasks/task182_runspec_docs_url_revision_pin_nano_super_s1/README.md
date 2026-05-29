# task182_runspec_docs_url_revision_pin_nano_super_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=3 -->

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
- PR: https://github.com/songCNMS/Nemotron/pull/289
- Tested/merged exact head: `6126f54dac84d4b101a01860a383926a31a24b69`
- Superseded head: `e304af202a5f32417f30ba4010ad27d0785fb9a1`
- Merge SHA: `90b3122c5b803ed0192ac0dab273473da6a3c52f`
- Validated implementation head: `daea92a02ba9cf6b7dbb211560cec91197ca88b7`
- Checks: focused static pytest, py_compile, Ruff on the new test,
  structured static probe, product-scope stale URL grep, added-line
  live-surface scan, `git diff --check`, and `git diff --cached --check`
  passed.
- Merged-main verification: focused runspec Nano/Super pytest 3 passed,
  py_compile touched recipe/test files, Ruff focused test, diff checks, and
  `PM_MERGED_RUNSPEC_NANO_SUPER_DOCS_URL_PROBE_PASS`.
