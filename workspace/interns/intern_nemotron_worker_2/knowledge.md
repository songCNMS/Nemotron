# intern_nemotron_worker_2 - personal knowledge base

<!-- METADATA:SESSION=3 -->

---

## Knowledge entries

1. task337 runtime gate: Qwen3 MoE Bridge import can be remediated without
   system/shared-root mutation by prepending a task-owned runtime target that
   contains `megatron-energon==7.3.2` plus its missing import dependencies.
   This only supports no-training preflight reruns; it does not release
   task310/all-SFT 30B training.
