# task286_qwen_aime_v11_task285_smoke_gate_review_s1 - Task Knowledge

<!-- METADATA:SESSION=22 -->

## Knowledge Entries

1. task286 is read-only review of task285 smoke evidence, not training or eval
   execution.
2. A task285 smoke checkpoint is not acceptable unless it proves real Qwen3-4B
   base load/import, first-step LR `> 0`, finite loss, and task-owned artifact
   retention.
3. task276 sparse valid/test risk must remain a carried residual risk and must
   not be used to make model-quality claims.
4. Even task286 approval can only release a later non-AIME canary gate. Corrected
   AIME2025 same-harness comparison remains blocked until canary passes and a
   reviewed FT artifact exists.
5. Until task285 has an official branch/PR/artifact report with exact head and
   artifact root, the only valid task286 disposition is HOLD.
6. A task285 blocker should be classified precisely as dependency/runtime,
   base-load/import, data-contract, zero-LR, random-init signal, resource, or
   artifact evidence.
7. Task286 review must not treat sparse task276 valid/test evidence as model
   quality support, and must verify no AIME2025 prompt/label train leakage or
   task255 reuse before approving any later non-AIME canary eligibility.
