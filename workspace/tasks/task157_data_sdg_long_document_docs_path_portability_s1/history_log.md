# History Log

<!-- METADATA:STATUS=Working,TASK=task157_data_sdg_long_document_docs_path_portability_s1,ROLE=dev,SESSION=1 -->

## 2026-05-29

- Started task157 from `origin/main` at `0b31358436c38e698c7c2bc3a89871df273df21c`.
- Updated scoped long-document SDG docs/comments toward `${NEMO_RUN_DIR:-.}/output/data/sdg/long-document/...` portability.
- Added focused static docs test coverage.
- Ran focused static docs pytest, py_compile, Ruff, scoped no-`/lustre/` grep, structured portable examples probe, added-line live-surface scan, `git diff --check`, and `git diff --cached --check`.
- Opened PR #266: https://github.com/songCNMS/Nemotron/pull/266
- PM reported PR #266 independently gated, squash-merged, and verified on main at merge commit `2cb891846c6f86d8917cd6289070c687dfdd6f91`; recorded closeout and returned dev status to idle.
