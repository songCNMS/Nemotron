# task076_qwen_v9_aime_recurrence_tuning - Task knowledge

<!-- METADATA:SESSION=8 -->

> **Writing rule**: one line each, format `N. category: content`
>
> Categories: supervisor request, technical fact, file change, research conclusion

---

## Knowledge entries

1. supervisor request: Start a V9 tuning task focused on recovering `aime_06`-style counting/recurrence behavior after task075 showed V8 failed AIME25 by one correct repeat.
2. technical fact: Task075 V8 corrected eval scored MMLU-Pro `0.5606715425531915`, AIME25 `0.19666666666666666`, and HMMT exact percent `13.333333333333334`.
3. technical fact: Task075 AIME audit found V8 had fewer AIME25 length caps than V7 (`14` vs `27`) but regressed on `aime_06` from V7 `10/10` correct to V8 `0/10` correct.
4. research conclusion: The V9 tuning hypothesis should target recurrence/counting answer quality rather than parser repair or larger generation budget.
5. technical fact: `aime_06` is equivalent to counting length-16 binary strings with exactly 8 ones and no substring `111`; the DP count is `2907`, so the required remainder is `907`.
6. research conclusion: V9 should preserve V8 clean-final filtering and add a focused recurrence/counting sidecar, rather than increasing `max_tokens` or changing exact-final-answer scoring.
7. file change: Added `hard_math_recurrence_v9` data-prep and Qwen scale-up planner support with V9-specific sidecar weights.
8. technical fact: V9 requires V8 clean-final hard-math rows plus recurrence/counting/run-length keyword signals.
9. technical fact: The existing V8 hard sidecar has `220/4546` rows passing the V9 recurrence filter.
10. file change: Generated local V9 scale-up plan at `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/scaleup_manifest.json`.
11. technical fact: The V9 decontamination corpus has `1479` prompts: `30` AIME25, `30` HMMT, and `1419` MATH-style heldout-eval prompts.
12. research conclusion: The V9 continuation plan should start from V8 `iter_0000779` with a short `0.05` epoch, low-LR recurrence sidecar run before any corrected full eval.
13. file change: Synced Session 6 bookkeeping after pushing the V9 recurrence strategy and decontaminated plan support.
14. technical fact: Session 7 uncapped M0 prep produced valid rows for all 11 agentic datasets and recorded `2389` known Hermes conversion errors.
15. file change: Optimized `decontaminate_math_rows` with an eval n-gram inverted index so V9 decontamination no longer performs a full rows-by-corpus nested scan.
16. technical fact: Session 7 M1 V9 prep produced `983087` train rows and `11354` val-shadow rows after dropping `310` decontamination blockers from base math train and `310` from sidecar math train.
17. technical fact: The final V9 recurrence sidecar contains `221` hard verified full-solution training rows; heldout eval rows remain excluded from training at `1419`.
18. supervisor request: Use `/mnt/cephfs/data/stable/models/Qwen` instead of the inaccessible `/mnt/3fs` Qwen path for the model checkpoint/tokenizer path.
19. technical fact: The usable cephfs Qwen 30B-A3B Instruct tokenizer/model directory is `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
20. technical fact: V9 packing completed with `32` shards, `983135` total sequences, `667289202` total tokens, `pack_size=8192`, and tokenizer URI `file:///mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
21. technical fact: The V9 training manifest uses V8 checkpoint `iter_0000779`, `train_iters=192`, `global_batch_size=8`, `seq_length=8192`, LR `8e-8`, min LR `3e-8`, warmup `20`, and `qwen3_30b_a3b_local_train.py`.
22. technical fact: The generated `m1_basket` eval dry-run compiled successfully with `adlr_aime25` and `enable_thinking=false`.
23. technical fact: NemTron did not have `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` mounted, so Session 8 mirrored only Qwen HF metadata/tokenizer files there and excluded the 16 `model-*.safetensors` weight shards.
24. technical fact: Qwen3 30B-A3B recipe builder preflight passed with the lightweight HF metadata/tokenizer mirror because the HF bridge uses `load_weights=False` and the actual weights load from V8 NeMo checkpoint `iter_0000779`.
25. technical fact: V9 training completed all `192` iterations on NemTron 8xH200 and saved final checkpoint `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000192`.
26. technical fact: V9 train loss decreased from iter 10 lm loss `12.25112` to iter 190 lm loss `8.950349`; final validation loss at iter 192 was `8.960094`.

---
