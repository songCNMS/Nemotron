# task180_doc_intelligence_mmlongbench_pdf_revision_pin_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Pin the doc-intelligence notebook MMLongBench-Doc PDF root from floating
  `resolve/main/documents` to exact dataset revision
  `2ff6aa9237fc777b6627dc57a486e9225ac5fb86`.
- Preserve the three registered demo PDF filenames and local-first `_ensure_pdf`
  behavior.
- Add focused static notebook JSON coverage.

## Boundaries

- Static notebook/test/docs only.
- No notebook execution, `requests.get`, PDF download, Hugging Face calls, NIM
  or endpoint inference, data prep, train/eval, W&B, cluster jobs, deploy,
  artifact operations, main push, or self-merge.

## Status

- Base: `67bb428e4a992c608b8795795ced4f3fa9b9271c`
- Branch: `intern_nem_dev_1/task180_doc_intelligence_mmlongbench_pdf_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/287
- Merge SHA: `510b6eec33edece3d212a3187b16db3d1b4a8a15`
- Ready-for-gate head: `7a1c99badec0c803901f27e905e9098547008654`
- Validated implementation head: `4161794c853d93c4e55a769c63dbb1b8484c1c84`
- Checks: focused notebook pytest, py_compile, Ruff, structured notebook probe, added-line live-surface scan, and diff checks passed.
- Merged-main verification: PM gate, independent exact-head test, final exact-ref check, and merged-main verification passed.
