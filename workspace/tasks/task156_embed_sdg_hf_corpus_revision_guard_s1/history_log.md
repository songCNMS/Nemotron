# task156_embed_sdg_hf_corpus_revision_guard_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Accepted PM assignment and created branch
  `intern_nem_dev_3/task156_embed_sdg_hf_corpus_revision_guard_s1`
  from `origin/main` at `795eb92359257ed82816a8685db0f9cae1c751ae`.
- Updated Embed Stage0 SDG `hf://` corpus parsing to require a
  40-character lowercase commit SHA revision before importing/calling
  `snapshot_download`.
- Updated focused HF corpus URI tests to preserve local path and pinned
  default URI behavior while rejecting unpinned or floating refs without
  calling `snapshot_download`.
- Verified focused pytest, `py_compile`, Ruff, structured mock no-download
  probe for unpinned/floating refs, and `git diff --check` before staging.
- Opened PR #263 to `main`: https://github.com/songCNMS/Nemotron/pull/263.
