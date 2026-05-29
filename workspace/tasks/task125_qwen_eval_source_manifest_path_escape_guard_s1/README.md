# task125_qwen_eval_source_manifest_path_escape_guard_s1

## Scope

- Harden Qwen eval reproduction gate source-manifest validation so accepted
  paths are normal repo-relative files resolved under `REPO_ROOT`.
- Reject absolute paths, empty or whitespace paths, `.`, `..`, empty path
  components, symlink escapes, directories, and missing files.
- Preserve the current production `qwen_eval_repro_gate.yaml` and existing
  benchmark-alignment source-manifest behavior.
- Add focused synthetic tests in `tests/recipes/super3/test_qwen_eval_repro_gate.py`.

## Boundaries

- No live benchmark/eval runs, endpoint calls, W&B, cluster jobs, deployments,
  data prep, training, artifact downloads, direct `main`/`master` push, or
  self-merge.

## Status

- Branch: `intern_nem_dev_3/task125_qwen_eval_source_manifest_path_escape_guard_s1`
- Base: `dc6e00e741c4189051bc4db4052283dbc78d0c13`
- PR: https://github.com/songCNMS/Nemotron/pull/232
