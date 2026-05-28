# task076_qwen_v9_aime_recurrence_tuning - Qwen V9 AIME recurrence tuning

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

Task075 evaluated Qwen3-30B-A3B V8 `iter_0000779` with the corrected V7 gate protocol. V8 passed MMLU-Pro and HMMT, but failed AIME25 by one correct repeat: `59/300 = 0.19666666666666666` against the `>=0.20` threshold.

The row-level audit showed this is not a scorer or length-cap artifact. V8 improved AIME25 parsing and length behavior versus V7, but regressed on `aime_06`: V7 answered all 10 repeats correctly, while V8 answered all 10 repeats incorrectly. The problem is a chair-subset counting recurrence, so V9 should specifically recover recurrence/counting behavior without losing V8's improvements on `aime_14` and length-capped rows.

## Source Artifacts

- V8 eval report: `workspace/tasks/task075_qwen_v8_export_eval/qwen_v8_iter0779_corrected_eval_session3.md`
- V8 AIME audit: `workspace/tasks/task075_qwen_v8_export_eval/qwen_v8_aime25_v7_comparison_session4.md`
- V7 math results: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session91_corrected_eval/outputs/math_corrected_full/results.jsonl`
- V8 math results: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/outputs/math_corrected_full/results.jsonl`
- V8 checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`

## Goals

- Build a V9 tuning plan that targets AIME-style counting/recurrence failures, starting from the `aime_06` regression pattern.
- Produce a small, decontaminated recurrence/counting sidecar or weighting change that can be mixed into the existing Qwen hard-math SFT flow.
- Train or prepare a V9 candidate checkpoint from the V8 lineage, with run scripts and artifact paths recorded.
- Run a targeted corrected AIME recurrence smoke before the expensive full corrected eval.
- If the targeted smoke is promising, export the V9 checkpoint to HF and run the corrected MMLU-Pro/AIME25/HMMT gate protocol.

## Acceptance Criteria

- [x] V7/V8 AIME row audit is converted into a concrete V9 tuning hypothesis, including why `aime_06` failed and what data or weighting should address it.
- [x] V9 data or training plan is generated with explicit decontamination against AIME25/HMMT/MATH-style heldouts.
- [x] V9 candidate checkpoint or a clearly blocked launch record exists with exact commands, logs, and artifact paths.
- [x] Targeted recurrence/counting AIME smoke records per-row predictions for `aime_06`-style prompts.
- [x] If a V9 checkpoint is produced, HF export passes config/tokenizer/shard validation.
- [ ] If a V9 checkpoint is produced, corrected full MMLU-Pro, AIME25 `max_tokens=8192`, and HMMT `max_tokens=8192` metrics are recorded and compared with V7/V8.

## Session 1 Result

- Branch: `intern_nemontron_code_reading/task076_qwen_v9_aime_recurrence_tuning`.
- PR: `https://github.com/songCNMS/Nemotron/pull/183`.
- Hypothesis report: `workspace/tasks/task076_qwen_v9_aime_recurrence_tuning/v9_tuning_hypothesis_session1.md`.
- Initial direction: add a high-precision `hard_math_recurrence_v9` sidecar on top of V8 clean-final rows, selected for recurrence/counting structure and still gated by AIME25/HMMT/MATH decontamination.

## Session 2 Result

- Added `hard_math_recurrence_v9` prep/planner support and tests.
- Generated report: `workspace/tasks/task076_qwen_v9_aime_recurrence_tuning/v9_data_plan_session2.md`.
- Generated local V9 plan: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/scaleup_manifest.json`.
- Generated decontamination corpus: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/aime25_hmmt_math_heldout_decontam_corpus.jsonl` with `30` AIME25, `30` HMMT, and `1419` MATH-style heldout prompts.
- Source-count probe found `220/4546` existing V8 hard sidecar rows match the V9 recurrence/counting filter.
- Training was not launched in Session 2.

## Session 7 Result

- Generated report: `workspace/tasks/task076_qwen_v9_aime_recurrence_tuning/v9_data_prep_session7.md`.
- Optimized V9 math decontamination and completed M1 prep: `983087` train rows, `11354` val-shadow rows, `310` dropped math blockers in base train and `310` in sidecar train.
- V9 recurrence sidecar: `221` hard verified full-solution training rows; `1419` heldout eval rows remain excluded.
- Switched Qwen model/tokenizer path from inaccessible `/mnt/3fs` to `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Packed data: `32` shards, `983135` total sequences, `667289202` total tokens, `pack_size=8192`; Qwen chat contract validation passed.
- Generated training plan: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/training_plan/task076_qwen30b_a3b_hard_math_recurrence_v9/training_manifest.json` with `train_iters=192`.
- Ran generated `m1_basket` eval dry-run successfully; training launch remains the next step.

## Session 8 Result

- Generated report: `workspace/tasks/task076_qwen_v9_aime_recurrence_tuning/v9_train_session8.md`.
- Synced repo and packed V9 artifacts to NemTron.
- Created a lightweight metadata/tokenizer mirror at `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` on NemTron because the cephfs mount was not present there.
- Launched and completed V9 training: `192/192` iterations on 8 H200 GPUs from V8 checkpoint `iter_0000779`.
- Final checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000192`.
- Final validation loss at iter 192: `8.960094`; no traceback/OOM/runtime error was found in the observed train log.

## Session 9 Result

- Generated report: `workspace/tasks/task076_qwen_v9_aime_recurrence_tuning/v9_export_smoke_session9.md`.
- Exported final V9 checkpoint `iter_0000192` to HF at `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/hf_export_iter_0000192`.
- Used the user-requested Qwen metadata/tokenizer path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- HF validation passed: `16` safetensors shards, `61066575144` safetensors bytes, `qwen3_moe`, `48` layers, `128` experts, `8` experts per token, tokenizer `Qwen2TokenizerFast`, chat template present.
- Served the HF export with SGLang `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`.
- Targeted corrected `aime_06` smoke completed all `10` repeats with expected answer `907`, but all `10` hit `finish_reason=length`, parsed `0/10`, correct `0/10`, and averaged `8192` completion tokens.
- Minimal chat smoke also degenerated (` the   the the the the the`), so full corrected MMLU-Pro/AIME25/HMMT was not launched; next step is diagnosing V9 training/export lineage before spending the full gate.

## Session 10 Result

- Generated report: `workspace/tasks/task076_qwen_v9_aime_recurrence_tuning/v9_checkpoint_root_fix_session10.md`.
- Diagnosed Session 8/9 V9 as invalid: the launch exported `SUPER3_M1_PRETRAINED_CHECKPOINT` as the child path `.../checkpoints/iter_0000779`, but Megatron-Bridge expects the checkpoint root containing `latest_checkpointed_iteration.txt`.
- Confirmed evidence: invalid V9 log has no `successfully loaded checkpoint` line and trained at random-init scale (`iter 10` loss `12.25112`, final validation loss/PPL `8.960094/7786.093`).
- Fixed both training planners to normalize `iter_XXXXXXX` checkpoint paths to their parent checkpoint root and added regression tests.
- Launched corrected V9 rerun using the same packed V9 data and the corrected V8 checkpoint root `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints`.
- Corrected run loaded the V8 checkpoint successfully and completed `192/192` iterations with final validation loss/PPL `0.4252748/1.530011`.
- Corrected checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/checkpoints/iter_0000192`.
- The Session 9 HF export/smoke belongs to the invalid lineage; the corrected checkpoint still needs HF export and targeted `aime_06` smoke.
