# task264_qwen_aime_v11_eval_gate_canary_retention_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Accepted Qwen3-4B base score is `11/30` exact-normalized under the corrected
   same-harness AIME25 `30x1` protocol.
2. task260 found task255 FT had `0/30` parsed and mixed-script/code-token tails
   on all rows, so future artifacts need a non-AIME canary before AIME eval.
3. Existing task257 artifacts retained only `response_tail`; V11 should retain
   full completions or a deterministic debug transcript for forensic review.
4. This task cannot run live AIME eval or authorize promotion/30B.
5. A V11 canary must use synthetic non-AIME prompts only and should be
   documented with prompt-source hashes so reviewers can verify it is not
   train or held-out AIME data.
