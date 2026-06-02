# task300_qwen_aime_v11_30b_same_harness_testing_s1 - task knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. hard-gate: 30B FT acceptance requires same-harness FT score greater than or
   equal to the exact 30B base score.
2. sequence: base AIME2025 score first, then after training non-AIME canary,
   then corrected AIME2025 FT-vs-base.
3. boundary: AIME2025 is eval/decontam only and cannot enter training.
4. acceptance: worker_3 accepted task300 from `origin/main`
   `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`; task298 must define the exact
   30B model path and runtime/eval route before base scoring.
5. blocker: task298 has only an acceptance branch at
   `7d24b9295740ef5c21fd443d6399ec9641f8f5c5` with no visible route report or
   artifacts, so task300 must not launch 30B base endpoint/export/eval yet.
6. read-only proof: the candidate 30B model path exists on NemTron and eight
   H200s were idle, but this is not a substitute for task298's required
   runtime/eval route PASS.
