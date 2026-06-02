# task300_qwen_aime_v11_30b_same_harness_testing_s1 - task knowledge

<!-- METADATA:SESSION=76 -->

## Knowledge Entries

1. hard-gate: 30B FT acceptance requires same-harness FT score greater than or
   equal to the exact 30B base score.
2. sequence: base AIME2025 score first, then after training non-AIME canary,
   then corrected AIME2025 FT-vs-base.
3. boundary: AIME2025 is eval/decontam only and cannot enter training.
