# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Started task167 from `origin/main` at `07b55e3d96f36965a472a3b7eb89e5cc25c855fa`.
- Added MMPR-Tiny repo/revision constants and passed the pinned revision to both cookbook `hf_hub_download` calls.
- Replaced unsafe zip `extractall()` with `safe_extract_zip` plus direct-checkout import fallback.
- Added focused mocked/static tests for pinned downloads, malicious zip rejection, and normal synthetic zip extraction.
- Ran focused pytest, py_compile, Ruff, no-`extractall` grep, structured AST probe, added-line live-surface scan, and `git diff --check` without live HF/MMPR downloads or real conversion.
- Opened PR #274: https://github.com/songCNMS/Nemotron/pull/274
