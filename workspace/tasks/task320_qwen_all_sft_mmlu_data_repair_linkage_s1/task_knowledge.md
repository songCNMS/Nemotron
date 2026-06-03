# task320_qwen_all_sft_mmlu_data_repair_linkage_s1 - Task Knowledge

<!-- METADATA:SESSION=93 -->

## Knowledge Entries

1. Task314 found 92 MMLU-Pro losses and 90 gains for net `-2`; math gained
   `+13` while multiple non-math categories lost.
2. The next data repair should protect broad MMLU-Pro retention, not only math
   gains.
3. This task does not authorize training, eval, or packing.
4. Task320 linkage found non-math aggregate MMLU-Pro delta `-15`; `86/92`
   loss rows were outside math.
5. Future all-SFT data repair should add MMLU-Pro prompt/problem heldout hashes
   to decontam alongside AIME2025/HMMT/MATH, with zero accepted overlaps before
   packing.
6. Task319 is a blocking dependency for generic raw blend feasibility; until
   task319 is accepted, the safe state is
   `BLOCK_PACK_OR_TRAIN_RAW_BLEND_PENDING_TASK319`.
