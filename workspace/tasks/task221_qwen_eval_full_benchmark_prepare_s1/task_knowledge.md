# task221 Task Knowledge

- Qwen SGLang chat endpoint must receive `chat_template_kwargs.enable_thinking=false` and `chat_template_kwargs.truncate_history_thinking=false`; task210 showed message content can be null without these kwargs.
- The prepared endpoint route is slashless: `/v1/chat/completions` on port `13000`.
- The task210 staged model path is visible on NemTron but not on the local CPU mount. Use NemTron-side filesystem checks before serving.
- The current M1 executable path is the 14-task `m1_full_basket_launcher_available` config. The intended 19-task `m1_full_basket` still includes five targets without exact launcher mappings.
- The full 27-target plan is 19 M1 targets plus 8 M2 registry targets, but M2 remains config-only/runtime-deferred until assets, APIs/databases, sandboxes, and baselines are available.
- Local `/work-agents/.venv` does not have `nemo_evaluator_launcher`; official live eval should use a runtime that provides it, or PM must explicitly accept the task210 direct-wrapper fallback.
