# task251_qwen_aime_v10_hotpotqa_loader_unblock_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. #327 merged task248 as a blocked prep report, not as a Qwen3-4B go/no-go
   pass.
2. The current task248 blocker is `hotpotqa/hotpot_qa` under Hugging Face
   `datasets`, where `trust_remote_code` is no longer supported.
3. The smallest expected workaround is a task-owned standard-format HotpotQA
   cache or registry override, with source revision, rows, checksums, and split
   mapping recorded.
4. task251 must not introduce AIME2025 prompts or labels into trainable data;
   AIME2025 remains held out for eval/decontamination only.
5. Passing task251 local prep does not itself authorize task243 comparison,
   FT promotion, or 30B/8-GPU scale.
