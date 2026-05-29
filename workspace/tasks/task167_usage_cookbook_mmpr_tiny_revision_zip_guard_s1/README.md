# task167_usage_cookbook_mmpr_tiny_revision_zip_guard_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Pin usage-cookbook MMPR-Tiny `hf_hub_download` calls to revision `eb493212c9614b69ca49cd6e66719413c514459b`.
- Replace unsafe `ZipFile.extractall()` in the NeMo-Gym cookbook converter with the repo safe zip helper.
- Add focused mocked/static tests for pinned downloads and safe extraction behavior.

## Boundaries

- No live HF/MMPR download, real data conversion, train/eval, endpoint, W&B, cluster, deploy, artifact operations, main push, or self-merge.
- Scope is limited to the usage-cookbook converter, focused tests, and task/status docs.

## Status

- Base: `07b55e3d96f36965a472a3b7eb89e5cc25c855fa`
- Branch: `intern_nem_dev_1/task167_usage_cookbook_mmpr_tiny_revision_zip_guard_s1`
- PR: pending
