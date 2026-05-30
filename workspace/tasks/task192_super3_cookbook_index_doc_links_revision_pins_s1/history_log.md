# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-30

- Started task192 from `main` at
  `89a6da531c4c693da585a7cc9ac96c51492bffa4`.
- Scope is limited to the Super3 cookbook README, Super3 entries in
  `docs/deployment-guides.md`, focused static docs test coverage, and dev_3
  status/task docs.
- Boundaries recorded: no live git clone/fetch/checkout beyond normal repo
  sync, build/download, cookbook execution, recipe/data-prep/train/eval,
  endpoint, W&B, cluster, deploy, artifact operation, direct `main`/`master`
  push, or self-merge.
- Pinned four Super3 cookbook README self-repo `blob/main` links and five
  Super3 deployment-guide `tree/main` links to
  `89a6da531c4c693da585a7cc9ac96c51492bffa4`.
- Added focused static docs tests for exact pin coverage, stale scoped
  self-repo `main` link rejection, context preservation, and non-Super3
  deployment guide links staying out of scope.
- Ran focused pytest, py_compile, Ruff, structured static probe, added-line
  live-surface scan, `git diff --check`, and `git diff --cached --check`.
- Opened PR #299 to `main`: https://github.com/songCNMS/Nemotron/pull/299.
