# task165_data_blend_revision_propagation_s1 knowledge

<!-- METADATA:SESSION=1 -->

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
