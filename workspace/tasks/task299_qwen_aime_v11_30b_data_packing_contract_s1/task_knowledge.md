# task299_qwen_aime_v11_30b_data_packing_contract_s1 - task knowledge

<!-- METADATA:SESSION=81 -->

## Knowledge Entries

1. data: task276 V11 packed data can be reused for 30B only after tokenizer,
   chat-template, split parity, and decontamination are reproven for
   Qwen3-30B-A3B-Instruct.
2. boundary: AIME2025 prompts/labels remain held-out eval/decontam corpus only.
3. current finding: 4B and 30B Qwen tokenizer assets/API match in preliminary
   probes, but task276 raw packed metadata names the 4B tokenizer URI; final
   PASS needs a task-owned 30B-ready root or strict proof that the 30B launch
   contract accepts the adapted metadata.
