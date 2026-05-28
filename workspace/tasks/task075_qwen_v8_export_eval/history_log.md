# task075_qwen_v8_export_eval - History Log

<!-- METADATA:SESSION=2 -->

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
