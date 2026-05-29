# task157_data_sdg_long_document_docs_path_portability_s1

## Scope

- Replace concrete long-document SDG `/lustre/...` documentation examples with `${NEMO_RUN_DIR:-.}/output/data/sdg/long-document/...` examples.
- Keep command names, option names, stage names, and manual/auto-serve semantics unchanged.
- Add focused static coverage for the scoped README and OCR config comment.

## Boundaries

- No production Python, deployment YAML, CLI behavior, generated artifacts, or unrelated docs.
- No live long-document SDG data prep, `--serve` launch, endpoint calls, downloads, training, eval, W&B, cluster jobs, deploy, artifact transfer, main push, or self-merge.

## Status

- Base: `0b31358436c38e698c7c2bc3a89871df273df21c`
- Branch: `intern_nem_dev_1/task157_data_sdg_long_document_docs_path_portability_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/266
- Merge commit: `2cb891846c6f86d8917cd6289070c687dfdd6f91`
- Checks: focused static docs pytest, py_compile, Ruff, no-`/lustre/` grep, structured portable examples probe, added-line live-surface scan, and diff checks passed.
