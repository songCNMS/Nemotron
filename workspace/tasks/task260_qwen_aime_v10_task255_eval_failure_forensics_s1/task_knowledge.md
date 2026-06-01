# task260_qwen_aime_v10_task255_eval_failure_forensics_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. task260 is a read-only failure forensic task; it must not rerun AIME or train.
2. The task255 FT result to explain is `0/30 = 0.0`, parsed `0/30`, finish
   reasons `stop=7,length=23`.
3. The accepted base comparator is task247 Qwen3-4B `11/30` under the same
   corrected AIME2025 protocol.
4. AIME2025 remains held-out eval/decontam only.
5. Forensics should classify observed text only from existing `results.jsonl`
   artifacts; manual inspection may identify likely final-answer strings, but
   must not become a new eval run or a promotion/go-no-go claim.
