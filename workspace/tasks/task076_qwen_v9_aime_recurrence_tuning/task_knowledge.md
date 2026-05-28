# task076_qwen_v9_aime_recurrence_tuning - Task knowledge

<!-- METADATA:SESSION=11 -->

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
27. technical fact: V9 `iter_0000192` was exported to HF at `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/hf_export_iter_0000192` using source metadata/tokenizer `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
28. technical fact: V9 HF export validation passed with `16` safetensors shards, `61066575144` safetensors bytes, `qwen3_moe`, `48` layers, `128` experts, `8` experts per token, tokenizer `Qwen2TokenizerFast`, and chat template present.
29. technical fact: V9 targeted corrected `aime_06` smoke on `10` repeats used original prompts, `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`, and expected answer `907`; all `10` responses ended by length, parsed `0/10`, and correct was `0/10`.
30. research conclusion: V9 `iter_0000192` is not a useful full-gate candidate until lineage is diagnosed, because even a trivial chat smoke degenerated to repeated `the` tokens and `aime_06` produced no boxed answers.
31. technical fact: Session 10 diagnosed the invalid V9 as a checkpoint-root bug: the launch used child path `.../checkpoints/iter_0000779`, but Megatron-Bridge expects the checkpoint root containing `latest_checkpointed_iteration.txt`.
32. file change: Patched both Qwen scale-up and generic M1 SFT training planners to normalize `iter_XXXXXXX` checkpoint inputs to the parent checkpoint root before writing manifests or launch scripts.
33. technical fact: The corrected Session 10 V9 rerun loaded V8 checkpoint root `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints` and completed `192/192` iters with final validation loss/PPL `0.4252748/1.530011`.
34. technical fact: The corrected V9 checkpoint is `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/checkpoints/iter_0000192`; Session 9 HF export/smoke belongs to the invalid random-init lineage.
35. technical fact: Session 11 exported corrected V9 checkpoint-root-fix `iter_0000192` to HF path `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/hf_export_iter_0000192` using `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` as source HF metadata/tokenizer.
36. technical fact: The corrected V9 HF export validates with `16` safetensors shards, `61066575144` safetensors bytes, `qwen3_moe`, `48` layers, `128` experts, `8` experts per token, tokenizer `Qwen2TokenizerFast`, and chat template present.
37. technical fact: Corrected V9 SGLang serving used model id `task076-qwen3-30b-a3b-agentic-sft-hard-math-recurrence-v9-ckptroot-fix-s10-iter0000192-hf`, `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, and `max_running_requests=16`; minimal chat smoke returned exact `ready`.
38. technical fact: Corrected V9 targeted `aime_06` smoke with original prompts and expected answer `907` returned status `ok` and `finish_reason=stop` for all `10` repeats, parsed `10/10`, but correct remained `0/10`; predictions were five `640` and five `830`.
39. research conclusion: The checkpoint-root fix repaired the random-init generation pathology, but V9 still fails the recurrence recovery objective; a full corrected gate is not justified until the `aime_06` reasoning traces or V9 sidecar weighting are revised.

---
