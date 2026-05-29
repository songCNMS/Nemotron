# task162_long_document_public_docs_path_portability_s1

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Replace concrete `/lustre/...` examples in `docs/nemotron/data/sdg/long-document.md` with `${NEMO_RUN_DIR:-.}/output/data/sdg/long-document/...` examples.
- Preserve command names, option names, stage names, manual endpoint flow, `--serve` flow, and public-doc prose semantics.
- Add focused static docs coverage for the public page.

## Boundaries

- No production Python, deployment YAML, CLI behavior, generated artifacts, or unrelated docs.
- No live long-document SDG data prep, `--serve` launch, endpoint calls, downloads, train/eval, W&B, cluster jobs, deploy, artifact operations, main push, or self-merge.

## Status

- Base: `2cb891846c6f86d8917cd6289070c687dfdd6f91`
- Branch: `intern_nem_dev_1/task162_long_document_public_docs_path_portability_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/269
- Merge commit: `a9b324bf28cd6cb0470b58eec47fd17336fdec0f`
- Checks: focused static docs pytest, py_compile, Ruff, no-`/lustre/` grep, structured public-doc portability probe, added-line live-surface scan, and diff checks passed.
