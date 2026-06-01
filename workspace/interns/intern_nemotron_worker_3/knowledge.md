# intern_nemotron_worker_3 - personal knowledge base

<!-- METADATA:SESSION=4 -->

---

## Knowledge entries

1. task238 audit: when old recovery branches are superseded by later live evidence, preserve the old branches as historical references and recommend `covered/no recovery` rather than restoring docs or creating implementation tasks.
2. task238 audit: task216 -> task218 -> task219 -> task220 is sufficient train-side coverage for task203/task206/task209 because it moves past the old local/NemTron blockers and proves canonical single-GPU plus 8-H200 full-data one-iteration Qwen SFT checkpointing.
3. task243 AIME gate: corrected Qwen3-4B base-vs-FT comparison uses `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, `/v1/chat/completions`, Qwen tokenizer chat template with thinking disabled, exact-normalized accuracy over all request rows, and blocks FT judgment until same-harness base artifacts exist.
