# task274_qwen_aime_v11_data_safety_ready_review_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Runtime proof does not waive decontamination or held-out AIME2025 rules.
2. Future pilot data must preserve task262 split/sidecar fixes and avoid
   task255 failed/stale assumptions.
3. task274 is review-only; it must not create or modify trainable data, run
   training/eval/export/endpoint/promotion, use AIME2025 as train data, use
   30B/8-GPU, merge, push main, or delete shared files.
4. task274 disposition: source/decontamination evidence passes, but direct
   pilot use of currently visible packed data is blocked because task253
   `packed_qwen/splits` fails the merged task262 Qwen split guard.
5. Required next data-side action before any Qwen3-4B V11 pilot: rematerialize
   packed data from the task262 V11 blend plan under collision-safe split
   materialization and verify intended/exposed split equality plus no AIME2025
   train leakage.
