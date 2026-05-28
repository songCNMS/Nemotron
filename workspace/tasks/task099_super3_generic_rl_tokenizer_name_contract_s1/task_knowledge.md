# task099_super3_generic_rl_tokenizer_name_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=11 -->

## Knowledge Entries

1. assignment: generic Super3 stage2 RL `policy.tokenizer.name` must follow
   `${policy.model_name}` unless an operator explicitly overrides a separate
   tokenizer artifact.
2. technical fact: stage-specific Super3 RL configs already use
   `policy.tokenizer.name: ${policy.model_name}`; task099 aligns the generic
   default/tiny path with that contract.
3. test contract: raw generic default/tiny YAML must not contain
   `NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16` as the tokenizer default and must
   keep Qwen chat kwargs, stop string, tool parser, reasoning parser, and parser
   plugin checks green.
