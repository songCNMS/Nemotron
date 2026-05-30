# Task Knowledge

<!-- METADATA:SESSION=3 -->

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
- PR #309 merged to `main` as
  `f65dafdb15b28342c1fbd4a5ead807052bcdd264` after replacement exact-head
  gate PASS on final PR head `0880c34fe80e15a2c43c01d92fc6a5a724ae48f2`.
