# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task209 Session 6 failure log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session6/logs/02_session6_canonical_one_iter_torchrun.log`.
- Failure signature:
  `TypeError: MambaModel.forward() got an unexpected keyword argument
  'packed_seq_params'`.
- The crash occurs after the training loop starts in
  `megatron.bridge.training.gpt_step._forward_step_common`, at
  `output_tensor = model(**forward_args)`.
- `src/nemotron/recipes/super3/stage1_sft/config/test.yaml` drives
  `test_train.py` for the canonical single-GPU tiny SFT smoke and includes
  `dataset.packed_sequence_specs`, which triggers the upstream packed sequence
  forward arguments.
- Compatibility rule: keep `packed_seq_params` for model forward chains that
  explicitly accept it; drop it only when common `.module` unwrapping reaches a
  leaf forward that does not accept the keyword.
