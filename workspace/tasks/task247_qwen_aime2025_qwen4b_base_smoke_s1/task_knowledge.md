# task247_qwen_aime2025_qwen4b_base_smoke_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. Same-harness base score is mandatory before any FT checkpoint can be judged.
2. The approved Qwen3-4B checkpoint/tokenizer path is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
3. Parsed rate and finish reasons are diagnostics only; the gate uses
   exact-normalized accuracy over all request rows.
4. In SGLang, serving Qwen3 with `--reasoning-parser qwen3` can return text in
   `message.reasoning_content` while `message.content` is `null`; the task243
   runner expects `message.content`, so the valid task247 endpoint was launched
   without the reasoning parser.
5. The task247 base pilot artifact uses a task-owned `opencompass/AIME2025`
   cache pinned to revision `a6ad95f611d72cf628a80b58bd0432ef6638f958`, with
   `30` unique problems and one request per problem.
