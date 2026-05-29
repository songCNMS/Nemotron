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
- PR: pending
