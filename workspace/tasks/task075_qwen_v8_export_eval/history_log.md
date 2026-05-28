# task075_qwen_v8_export_eval - History Log

<!-- METADATA:SESSION=4 -->

## Session 1

- Created task from user request: export V8 `iter_0000779` to HF, serve with SGLang 16k context, and run corrected full MMLU-Pro/AIME25/HMMT eval against the V7 gates.
- Branch: `intern_nemontron_code_reading/task075_qwen_v8_export_eval`.
- PR: `https://github.com/songCNMS/Nemotron/pull/182`.
- Source checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`.
- Planned protocol: SGLang `tp=4`, `dp=2`, `context_length=16384`; AIME25/HMMT `max_tokens=8192`.

## Session 2

- Restarted Claude intern `intern_nemontron_review_cc` in tmux session `intern_nemontron_review_cc`.
- Verified pane command `claude`, child process `claude --permission-mode bypassPermissions`, and local Feishu daemon online status.
- Task075 export/eval work remains in progress; no eval artifacts changed in this turn.

## Session 3

- Found completed remote HF export at `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/hf_export_iter_0000779` and validated config/tokenizer/shards/manifest.
- Served the V8 export with SGLang `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`; `/v1/models` reported `max_model_len=16384`, and chat smoke returned exact `ready`.
- Ran corrected full MMLU-Pro: `6746/12032`, accuracy `0.5606715425531915`, parsed rate `1.0`.
- Ran corrected full AIME25 with original prompts and `max_tokens=8192`: `59/300`, accuracy `0.19666666666666666`, parsed rate `0.9533333333333334`.
- Ran corrected full HMMT with original prompts and `max_tokens=8192`: `4/30`, exact percent `13.333333333333334`, parsed rate `0.6666666666666666`.
- Recorded report `qwen_v8_iter0779_corrected_eval_session3.md`; overall V7-gate verdict is fail because AIME25 is below `0.20` by one correct repeat.
- Stopped the V8 SGLang endpoint after eval and verified GPUs returned to idle.

## Session 4

- Compared V8 AIME25 row-level results against V7 session91 using the same corrected original-prompt protocol.
- Recorded audit report `qwen_v8_aime25_v7_comparison_session4.md`.
- Found V8 improved length/parse behavior versus V7 (`14` length-capped rows versus `27`; `286` parsed rows versus `273`), so the AIME25 miss is not primarily a truncation artifact.
- Found exact-correct overlap: `51` both correct, `229` both wrong, `12` V7-only correct, `8` V8-only correct, net `-4` for V8.
- Identified the main real regression: `aime_06` dropped from V7 `10/10` correct to V8 `0/10` correct, with wrong final boxed predictions and no expected answer contained.
- Conclusion: keep V8 marked as a real AIME25 gate failure; do not treat the `59/300` result as scorer noise.
