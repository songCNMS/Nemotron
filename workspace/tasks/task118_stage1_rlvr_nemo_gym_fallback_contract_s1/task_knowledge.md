# task118_stage1_rlvr_nemo_gym_fallback_contract_s1 knowledge

<!-- METADATA:SESSION=16 -->

## Working Notes

- Stage1 RLVR should match sibling Stage2 RL training scripts: missing
  `nemo_gym_example_to_nemo_rl_datum_spec` is an environment/package problem,
  not a condition to hide with an empty local datum.
- A local fallback that creates empty `message_log` content can silently drop
  M0/RLVR bridge `responses_create_params.input` payloads.
- `stop_strings=None` is unsafe for Qwen RL paths because the expected stop
  contract is explicit `<|im_end|>` termination from the NeMo-Gym converter.
