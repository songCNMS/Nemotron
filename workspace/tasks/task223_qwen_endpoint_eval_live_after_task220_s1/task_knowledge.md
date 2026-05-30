# task223 Task Knowledge

- For this SGLang runtime, `/v1/health` returned 404 while `/health` and `/v1/models` returned 200. Use `/health` or `/v1/models` for readiness unless product routing changes.
- Qwen chat requests still require `chat_template_kwargs.enable_thinking=false` and `chat_template_kwargs.truncate_history_thinking=false` to produce non-null content.
- The local CPU and NemTron can have different visibility for task-owned files under the same cephfs path. Write endpoint launch/request artifacts on the host that will execute them, then copy small evidence files back if needed.
- The SGLang wrapper shell PID may exit without stopping the child Python listener. Cleanup must verify the child process command matches the task-owned model path and port before terminating it.
- Do not run the M1 launcher-available subset unless an approved runtime with `nemo_evaluator_launcher` is available.
