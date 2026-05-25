# task072_qwen_eval_repro_gate - History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-25 - intern_nem_dev_1

- PM assigned critical Qwen-first chat-template gate from synced `main` at
  `9456469509539648a5a2ab4e4b36a16fa46a95dd`.
- Created branch `intern_nem_dev_1/task072_qwen_eval_repro_gate_s1`.
- Scope accepted: own base-Qwen eval reproduction gate/evidence and do not
  treat `super3.jinja` consistency as sufficient.
- Probed known local Qwen endpoint routes:
  - `curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/models`
    -> connection refused.
  - `curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/health`
    -> connection refused.
  - `curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:30000/v1/models`
    -> connection refused.
- Implemented a sandbox gate manifest and validator that records Qwen model,
  tokenizer/chat-template reference behavior, chat-completions route,
  `chat_template_kwargs`, max generation tokens, parser/final-answer contract,
  raw artifact paths, baseline deltas, invalid legacy surfaces, and endpoint
  blocker probes.
- Validation:
  - `PYTHONPATH=src pytest -q tests/recipes/super3/test_qwen_eval_repro_gate.py tests/recipes/super3/test_eval_chat_template_kwargs.py tests/recipes/super3/test_m1_eval_full_basket.py`
    -> 58 passed, 9 warnings.
  - `python -m py_compile src/nemotron/recipes/super3/milestones/m1_eval_basket/__init__.py src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_eval_repro_gate.py`
    -> passed.
  - `git diff --check` -> passed.
- Residual blockers: fresh live Qwen endpoint smoke is blocked in this
  workspace by unavailable local endpoints; cluster/GPU endpoint launch,
  Docker/eval container execution, credentials, W&B publication, and official
  Qwen benchmark reproduction are outside this PR.
