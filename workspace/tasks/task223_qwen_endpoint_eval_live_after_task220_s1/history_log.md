# task223 History Log

## 2026-05-30

- Created evidence branch `intern_nem_dev_3/task223_qwen_endpoint_eval_live_after_task220_s1` from `origin/main` at `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Ran read-only NemTron preflight: PASS.
- Started one task223-owned SGLang endpoint from the task210 staged Qwen model path after correcting command-file visibility for NemTron.
- Verified endpoint readiness with `/health` and `/v1/models`.
- Ran one sanitized `/v1/chat/completions` request with `max_tokens=8`, no benchmark prompt, and Qwen `chat_template_kwargs`; PASS with content `OK`.
- Confirmed official launcher runtime is blocked in local `/work-agents/.venv`; ran the task210 direct corrected-math wrapper fallback for AIME/HMMT limit 1; PASS 2/2 parsed/correct.
- Held M1 launcher-available subset and full 27-target benchmark.
- Cleaned up task223-owned SGLang and verified no `:13000` listener, no SGLang processes, no H200 compute apps, and all H200s idle.
