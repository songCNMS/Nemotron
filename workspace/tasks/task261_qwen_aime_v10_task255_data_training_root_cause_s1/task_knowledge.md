# task261_qwen_aime_v10_task255_data_training_root_cause_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. task261 is a read-only data/training root-cause audit after task255 failed
   AIME with FT `0/30` versus base `11/30`.
2. The audit should inspect task253 packed shards, task255 logs/configs, and
   downstream task257 failure evidence.
3. It must not train, rerun eval, alter artifacts, or authorize promotion or
   30B/8-GPU.
4. Any V11 pilot recommendation must preserve AIME2025 as held-out eval and
   require same-harness base-vs-FT comparison.
