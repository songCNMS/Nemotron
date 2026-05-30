# task226 Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task221 prepared the Qwen eval continuation and established the intended 27-target plan: 19 M1 targets plus 8 M2 targets.
- Task223 verified SGLang can serve the staged Qwen model on `/v1/chat/completions` when Qwen `chat_template_kwargs.enable_thinking=false` and `truncate_history_thinking=false` are included.
- Current M1 subset release blocker is the official evaluator runtime: local `/work-agents/.venv` lacks `nemo_evaluator_launcher`.
- The M1 14-target subset should not run until task225 supplies an approved runtime and PM re-releases live benchmark work.
- The full 27-target benchmark remains blocked by five missing M1 exact launcher mappings and all M2 live asset/API/database/sandbox/baseline gaps.
