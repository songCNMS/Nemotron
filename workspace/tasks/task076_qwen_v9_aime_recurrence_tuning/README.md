# task076_qwen_v9_aime_recurrence_tuning - Qwen V9 AIME recurrence tuning

<!-- METADATA:STATUS=Open,ASSIGNEE= -->

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

- [ ] V7/V8 AIME row audit is converted into a concrete V9 tuning hypothesis, including why `aime_06` failed and what data or weighting should address it.
- [ ] V9 data or training plan is generated with explicit decontamination against AIME25/HMMT/MATH-style heldouts.
- [ ] V9 candidate checkpoint or a clearly blocked launch record exists with exact commands, logs, and artifact paths.
- [ ] Targeted recurrence/counting AIME smoke records per-row predictions for `aime_06`-style prompts.
- [ ] If a V9 checkpoint is produced, HF export passes config/tokenizer/shard validation.
- [ ] If a V9 checkpoint is produced, corrected full MMLU-Pro, AIME25 `max_tokens=8192`, and HMMT `max_tokens=8192` metrics are recorded and compared with V7/V8.
