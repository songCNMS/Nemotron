# task165_data_blend_revision_propagation_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Closeout Notes

- PR #273 was merged and verified on `main` at
  `0e190d301348990990650449485aa057eb7405ce`.
- Local `main` has been synced to the verified merge commit.
- No new product behavior was added in Session 2; this session is closeout
  bookkeeping only.

## Working Notes

- `DataBlend.Dataset.revision` already existed before this task; the missing
  contract was propagation into generic pretrain/SFT planning and lineage.
- `DatasetConfig.revision` is consumed by discovery, so both
  `PretrainPlanAdapter.to_plan_request()` and `SftPlanAdapter.to_plan_request()`
  must pass `item.revision`.
- `setup_pretrain_run()` and `setup_sft_run()` must include dataset `revision`
  fields in the deterministic `run_config`, including explicit `None`, so source
  revision changes affect `run_hash`.
- `InputDatasetInfo` already supports `revision`; artifact constructors only
  needed to pass through `d.revision`.
- The focused tests monkeypatch tokenizer resolution and call setup/adapters only;
  they do not invoke HF discovery, download stages, or full data-prep pipelines.
