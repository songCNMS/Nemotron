# task164_long_document_finepdfs_revision_pin_s1

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Pin long-document SDG FinePDFs seed loading to revision `220bac3acbf07789502c621d2d33952f51ac7f86`.
- Keep `HuggingFaceFW/finepdfs`, subset behavior, and downstream stage semantics unchanged.
- Add focused static/AST tests that do not call `load_dataset` or download PDFs.

## Boundaries

- No live `load_dataset`, PDF downloads, seed generation, `--serve`, endpoints, train/eval, W&B, cluster jobs, deploy, artifact operations, main push, or self-merge.
- Scope is limited to the seed script/config, focused static tests, and task/status docs.

## Status

- Base: `a9b324bf28cd6cb0470b58eec47fd17336fdec0f`
- Branch: `intern_nem_dev_1/task164_long_document_finepdfs_revision_pin_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/271
- Merge commit: `83119f9ca83a4978773f4702ef0a4b48c0c4fe94`
- Checks: focused static pytest, py_compile, Ruff, structured AST probe, added-line live-surface scan, and diff checks passed.
