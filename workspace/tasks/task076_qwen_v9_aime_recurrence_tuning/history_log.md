# task076_qwen_v9_aime_recurrence_tuning - History log

<!-- METADATA:SESSION=10 -->

---

## Session 0 - 2026-05-28 - Init

**Executor**: intern_nemontron_code_reading

Task created from the task075 V8 gate failure. Scope is V9 tuning focused on recovering AIME25 recurrence/counting behavior, especially the `aime_06` drop from V7 `10/10` correct to V8 `0/10` correct.

---

## Session 1 - 2026-05-28 - Accept and hypothesis

**Executor**: intern_nemontron_code_reading

- Created branch `intern_nemontron_code_reading/task076_qwen_v9_aime_recurrence_tuning` from `origin/main`.
- Opened PR `https://github.com/songCNMS/Nemotron/pull/183`.
- Accepted task by setting README metadata to `InProgress` and assignee to `intern_nemontron_code_reading`.
- Wrote `v9_tuning_hypothesis_session1.md`.
- Derived the correct `aime_06` recurrence: count length-16 binary strings with exactly 8 ones and no `111`; `dp[i][j][r]` with trailing run length `r` gives count `2907`, hence answer `907`.
- Proposed V9 direction: keep V8 clean-final filtering, then add a high-precision recurrence/counting sidecar selected for DP/subset/run-length/counting structure and protected by AIME25/HMMT/MATH decontamination.

---

## Session 2 - 2026-05-28 - V9 data plan support

**Executor**: intern_nemontron_code_reading

- Added `hard_math_recurrence_v9` to M1 Agentic SFT data prep and Qwen scale-up planner.
- Implemented V9 as a V8 clean-final hard-math subset filtered for recurrence/counting/run-length signals.
- Added V9 to the V7+ math decontamination guard.
- Added tests for V9 filtering, planner script emission, and decontamination guard behavior.
- Generated local decontamination corpus `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/aime25_hmmt_math_heldout_decontam_corpus.jsonl` with `1479` prompts.
- Generated local V9 scale-up plan `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/scaleup_manifest.json`.
- Wrote `v9_data_plan_session2.md` and marked the V9 data/training-plan acceptance criterion complete.

---

## Session 6 - 2026-05-28 - Checklist sync

**Executor**: intern_nemontron_code_reading

- Confirmed task076 PR branch was pushed through commit `89a9c1e`.
- Added the missing stop-hook Session 6 bookkeeping entry.
- Kept task status as Working because V9 data prep/training launch remains the next actionable step.

---

## Session 7 - 2026-05-28 - V9 local data prep and cephfs Qwen path

**Executor**: intern_nemontron_code_reading

- Ran uncapped M0 prep for the 11 agentic datasets; it produced valid rows for every dataset and recorded `2389` known Hermes conversion errors.
- Optimized V9 math decontamination by replacing the nested row-by-eval prompt scan with an eval n-gram inverted index; targeted tests passed before rerunning M1 prep.
- Completed M1 V9 prep with `983087` train rows and `11354` val-shadow rows; AIME25/HMMT/MATH-style decontamination scanned `859494` math rows and dropped `310` rows in both base train and sidecar train.
- Produced the V9 recurrence sidecar with `221` hard verified full-solution training rows and `1419` heldout eval rows.
- Regenerated the V9 Qwen scale-up plan with model/tokenizer path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` after local packing failed on inaccessible `/mnt/3fs`.
- Packed Qwen SFT data successfully: `32` shards, `983135` total sequences, `667289202` total tokens, `pack_size=8192`, tokenizer URI `file:///mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Passed Qwen packed chat contract validation and generated the V9 training manifest with `train_iters=192`, `train_rows=30699`, `valid_rows=2571`, LR `8e-8`, min LR `3e-8`, warmup `20`, and V8 checkpoint `iter_0000779` as the starting point.
- Ran the generated `m1_basket` eval dry-run; the config compiled with `adlr_aime25` present and `enable_thinking=false`.
- Wrote `v9_data_prep_session7.md`.

---

## Session 8 - 2026-05-28 - V9 NemTron training launch and completion

**Executor**: intern_nemontron_code_reading

- Synced the current PR branch and V9 packed output to NemTron with `sync_to_nemtron.sh`.
- Confirmed the user-requested Qwen path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` was not mounted on NemTron, then created a lightweight metadata/tokenizer mirror at the same path excluding the 16 HF safetensor weight shards.
- Verified the Qwen 30B-A3B recipe builder works with that lightweight HF metadata/tokenizer path because `load_weights=False` is used for the HF bridge and the actual weights load from the V8 NeMo checkpoint.
- Launched `run_nemtron_train.sh` in tmux session `task067_task076_qwen30b_a3b_hard_math_recurrence_v9` on 8 H200 GPUs.
- Training completed all `192/192` planned iterations from V8 checkpoint `iter_0000779`.
- Health signals: iter 10 train lm loss `12.25112`, iter 100 train lm loss `9.722968`, iter 190 train lm loss `8.950349`, validation loss at iter 100 `9.630936`, final validation loss at iter 192 `8.960094`.
- Checkpoints saved: `iter_0000100` and final `iter_0000192`.
- Final checkpoint path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000192`.
- Wrote `v9_train_session8.md`.

---

## Session 9 - 2026-05-28 - V9 HF export and targeted AIME06 smoke

**Executor**: intern_nemontron_code_reading

- Exported final V9 checkpoint `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000192` to HF path `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/hf_export_iter_0000192`.
- Used source HF metadata/tokenizer path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` and export log `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/logs/export_iter_0000192.log`.
- Validated the HF artifact: `16` safetensors shards, `61066575144` safetensors bytes, `model_type=qwen3_moe`, `48` layers, `128` experts, `8` experts per token, tokenizer `Qwen2TokenizerFast`, and chat template present.
- Wrote export manifest `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/hf_export_iter_0000192/task076_export_manifest.json`.
- Served the HF export in SGLang tmux session `task076_qwen_v9_iter0192_sglang_smoke` with `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, and `max_running_requests=16`.
- Ran targeted corrected `aime_06` smoke using the task071 corrected math runner row assignment and original AIME prompts. The expected answer was `907`; all `10` repeats returned status `ok` but hit `finish_reason=length`, parsed `0/10`, correct `0/10`, and averaged `8192` completion tokens.
- Recorded smoke artifacts under `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/targeted_smoke/aime06/`.
- Stopped the SGLang endpoint after smoke; port `30000` was clear and GPUs returned to idle.
- Wrote `v9_export_smoke_session9.md`.

---

## Session 10 - 2026-05-28 - Checkpoint-root diagnosis and corrected V9 rerun

**Executor**: intern_nemontron_code_reading

- Diagnosed the Session 8/9 V9 failure as a checkpoint path bug: `SUPER3_M1_PRETRAINED_CHECKPOINT` was set to `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`, but Megatron-Bridge expects the checkpoint root `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints`.
- Confirmed the invalid V9 log has no `successfully loaded checkpoint` line, while V8/V7 continuation logs do; invalid V9 trained at random-init scale with iter 10 lm loss `12.25112` and final validation loss/PPL `8.960094/7786.093`.
- Patched `plan_qwen_scaleup_run.py` and `plan_m1_agentic_sft_training.py` so `iter_XXXXXXX` checkpoint inputs are normalized to the parent checkpoint root before manifests and launch scripts are written.
- Added regression tests covering checkpoint-root normalization in both planner layers.
- Verification passed: `py_compile` for both planners, targeted pytest for the new normalization tests and related Qwen scale-up tests, and `ruff check` on touched planner/test files.
- Launched corrected V9 rerun at `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10` using the same V9 packed data, the cephfs Qwen metadata/tokenizer path, and the corrected V8 checkpoint root.
- Corrected rerun log confirms `successfully loaded checkpoint from /work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints [ t 1/4, p 1/2 ] at iteration 0`.
- Corrected rerun completed `192/192` iterations; health signals were iter 10 lm loss `0.4368270`, iter 100 lm loss `0.4449203`, iter 190 lm loss `0.4447130`, validation@100 loss/PPL `0.4531137/1.573203`, and final validation loss/PPL `0.4252748/1.530011`.
- Final corrected checkpoint path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/checkpoints/iter_0000192`; checkpoint marker is `192` and size is about `399G`.
- Wrote `v9_checkpoint_root_fix_session10.md`.

---
