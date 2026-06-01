# intern_nemotron_worker_3 - personal knowledge base

<!-- METADATA:SESSION=3 -->

---

## Knowledge entries

1. task238 audit: when old recovery branches are superseded by later live evidence, preserve the old branches as historical references and recommend `covered/no recovery` rather than restoring docs or creating implementation tasks.
2. task238 audit: task216 -> task218 -> task219 -> task220 is sufficient train-side coverage for task203/task206/task209 because it moves past the old local/NemTron blockers and proves canonical single-GPU plus 8-H200 full-data one-iteration Qwen SFT checkpointing.
3. task247 eval: serving Qwen3 through SGLang with `--reasoning-parser qwen3` can return completions in `message.reasoning_content` while `message.content` is `null`; the task243 AIME runner expects `message.content`, so use no reasoning parser for same-harness scoring.
4. task247 eval: the first Qwen3-4B base AIME2025 pilot artifact was `11/30` exact-normalized correct using `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, pinned `opencompass/AIME2025` cache revision `a6ad95f611d72cf628a80b58bd0432ef6638f958`, `8192` max tokens, `temperature=0.0`, and `top_p=1e-5`.
