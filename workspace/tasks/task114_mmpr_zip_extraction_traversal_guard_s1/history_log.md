# task114_mmpr_zip_extraction_traversal_guard_s1 - History Log

<!-- METADATA:SESSION=15 -->

## Session 1 - 2026-05-29

- Received PM assignment to guard MMPR zip extraction against archive path
  traversal.
- Started from local `main` fast-forwarded to `origin/main`
  `d64cbd067a15cca222b9eba200af1eb1ec5b7788` and created branch
  `intern_nem_dev_2/task114_mmpr_zip_extraction_traversal_guard_s1`.
- Added `nemotron.data_prep.utils.safe_zip` with pre-extraction member
  validation and safe member copying under the resolved extraction root.
- Replaced direct zip extraction in `prepare_public_mmpr_for_mpo.py`,
  `prepare_mmpr_tiny_for_vision_rl.py`, and `vlm_preference_prep.py`.
- Added focused synthetic zip tests for public MMPR, MMPR-Tiny, VLM stage, and
  the shared helper.
- Verified focused pytest, py_compile, Ruff, structured synthetic zip probe,
  and diff whitespace checks.
- Opened PR #222 to `main`: https://github.com/songCNMS/Nemotron/pull/222.
