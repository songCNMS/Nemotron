# task262_qwen_aime_v11_data_split_sidecar_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. task261 found the task253 exposed train split omitted intended M0 shards 5-6
   and hard-math shards 0-4 because dataset-qualified blend entries collapsed to
   basename symlinks.
2. V11 must not train until intended and exposed split rows/tokens/shards match
   or the pipeline fails closed before training.
3. AIME2025 prompts and labels are held-out eval/decontamination material only.
4. This task is data/packing readiness evidence only; it cannot authorize
   training, task243 comparison, promotion, or 30B/8-GPU.
