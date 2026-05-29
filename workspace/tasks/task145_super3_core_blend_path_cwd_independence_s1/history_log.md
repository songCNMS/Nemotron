# task145_super3_core_blend_path_cwd_independence_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Received PM assignment to make Super3 core repo-local source `blend_path`
  defaults CWD-independent.
- Started from local `main` synced to `origin/main`
  `802f7bee98579e5a9647813f5182bb048e1aa44b` and created branch
  `intern_nem_dev_2/task145_super3_core_blend_path_cwd_independence_s1`.
- Updated the listed Stage0 pretrain, Stage1 SFT, and Stage2 RL core
  data-prep YAML defaults to use repo-relative `src/nemotron/recipes/...`
  source blend paths instead of `${oc.env:PWD}/src/...`.
- Added repo-relative source-path resolution for the three Super3 data-prep
  config dataclasses, preserving absolute paths and arbitrary relative user
  overrides.
- Added focused static/config tests for non-repo CWD resolution, no listed
  `${oc.env:PWD}/src/` blend defaults, expected blend identities, and override
  preservation.
- Verified focused pytest, py_compile, Ruff, structured non-repo CWD
  resolution probe, static no-PWD-source-blend grep, and diff checks.
