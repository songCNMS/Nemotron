# task089_stage0_pretrain_data_prep_output_portability_s1 knowledge

<!-- METADATA:SESSION=8 -->

## Working Notes

- `tiny.yaml` already uses `${oc.env:PWD}/../output/super3/stage0_pretrain_tiny`
  and should remain distinct from the phase-specific production defaults.
- `default.yaml` is intentionally phase1-equivalent, so its portable
  `output_dir` should match `phase1.yaml`.
- The output-portability guard can remain static: this task does not require
  live tokenization, dataset downloads, W&B, or cluster execution.
- Session 8 added no new task089-specific implementation knowledge; task093
  owns the Nano3 stage3 eval chat-contract follow-up.
