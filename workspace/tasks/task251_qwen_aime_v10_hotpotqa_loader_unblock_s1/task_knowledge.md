# task251_qwen_aime_v10_hotpotqa_loader_unblock_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

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
6. PR #328 closed the HotpotQA `trust_remote_code` blocker for local M0/M1 prep
   and merged at `2026-06-01T19:27:31Z` from approved head
   `694197c81720dcc157518d8a86b2b5d7a7a2dd05` with merge commit
   `61fa65e9e9a535d531a65072c839760c3488207f`.
7. The worker branch-only closeout head
   `74155d22651f21be04e67463b05d3049077d0c47` records task completion after
   merge; it is not the PR evidence head.
8. The next blocker is `ModuleNotFoundError: No module named 'cosmos_xenna'`
   during Qwen packing; resolving that blocker may only produce local packing
   evidence until lead separately clears any training/eval step.
