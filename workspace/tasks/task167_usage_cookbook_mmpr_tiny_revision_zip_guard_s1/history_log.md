# History Log

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-29

- Started task167 from `origin/main` at `07b55e3d96f36965a472a3b7eb89e5cc25c855fa`.
- Added MMPR-Tiny repo/revision constants and passed the pinned revision to both cookbook `hf_hub_download` calls.
- Replaced unsafe zip `extractall()` with `safe_extract_zip` plus direct-checkout import fallback.
- Added focused mocked/static tests for pinned downloads, malicious zip rejection, and normal synthetic zip extraction.
- Ran focused pytest, py_compile, Ruff, no-`extractall` grep, structured AST probe, added-line live-surface scan, and `git diff --check` without live HF/MMPR downloads or real conversion.
- Opened PR #274: https://github.com/songCNMS/Nemotron/pull/274

## Session 2 - 2026-05-29

- PM reported PR #274 exact-head gated, squash-merged, and verified on merged `main`.
- Recorded tested head `5bdd117ebaeb605364786907f5d6822de1ab9a7e`, tested base `0e190d301348990990650449485aa057eb7405ce`, and merge commit `6328c018a86da7448e11a03bc1c71afc38e067f2`.
- Synced `origin/main` and local `main` to `6328c018a86da7448e11a03bc1c71afc38e067f2` without pushing main.
- Preserved no-live-run boundaries: no live HF/MMPR download, real conversion, train/eval, endpoint, W&B, cluster, deploy, artifact operation, main/master push, or self-merge.
