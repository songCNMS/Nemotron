# task280_qwen_aime_v11_sft_smoke_plan_hold_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. task280 is a no-run planning hold, not training authorization.
2. The future smoke must use task276 packed root and Qwen3-4B only.
3. AIME2025 data remains held-out eval/decontam only.
4. `stage1_sft/train.py` lazily writes Bridge `.npy` files next to the active
   packed split directory, so any released smoke must stage task276 packed data
   into a task280-owned run root before launch.
5. The current Qwen3-4B local train entrypoint sets tensor model parallel size
   2, so the bounded 4B smoke plan uses 2 GPUs rather than 1 GPU or forbidden
   30B/8-GPU scale.
6. task278/task279 approval and explicit lead release are hard gates; task280
   only records the exact fail-closed candidate plan.
