# task299_qwen_aime_v11_30b_data_packing_contract_s1 - task knowledge

<!-- METADATA:SESSION=84 -->

## Knowledge Entries

1. data: task276 V11 packed data can be reused for 30B only after tokenizer,
   chat-template, split parity, and decontamination are reproven for
   Qwen3-30B-A3B-Instruct.
2. boundary: AIME2025 prompts/labels remain held-out eval/decontam corpus only.
3. current finding: 4B and 30B Qwen tokenizer assets/API match in preliminary
   probes, but task276 raw packed metadata names the 4B tokenizer URI; final
   PASS needs a task-owned 30B-ready root or strict proof that the 30B launch
   contract accepts the adapted metadata.
4. final result: task-owned root
   `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`
   passed 30B tokenizer/chat-template, split parity, contract validation, and
   decontam proof; decision is `PASS_30B_DATA_PACKING_CONTRACT`.
5. final artifact top manifest sha256 is
   `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`.
6. PR #365 contains the final task299 docs/report closeout:
   `https://github.com/songCNMS/Nemotron/pull/365`.
7. PR #365 was lead-approved and self-merged at `2026-06-02T15:29:15Z`;
   merge commit `205fc919a643b1478964a9e91793247c5e821a38`, merged head
   `b8b760fb8f46cda8f302adbea106f19cc234e038`.
