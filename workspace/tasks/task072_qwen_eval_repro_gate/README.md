# task072_qwen_eval_repro_gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Goal

Define a Qwen-first eval reproduction gate before further chat-template
alignment work is accepted. Matching `super3.jinja` across stages is not
sufficient because the current target model is Qwen.

## Session 1 Scope

- Add a sandbox-runnable gate manifest and validator for base-Qwen eval
  reproduction evidence.
- Require Qwen checkpoint/tokenizer/chat-template provenance, endpoint type,
  chat route, `chat_template_kwargs`, generation budget, parser/final-answer
  contract, raw artifacts, and deltas against known repo-local Qwen baselines
  where available.
- Record legacy eval surfaces that are completions-only, short-generation
  capped, or parser-misaligned so they cannot be counted as valid Qwen-chat
  reproduction.
- Probe the known local Qwen endpoint route and record concrete blockers when
  the endpoint is unavailable.

## Out Of Scope

- Launching cluster eval or starting a GPU endpoint from this PR.
- Treating Super3 template consistency as a substitute for Qwen reference
  behavior.
- Publishing W&B artifacts or changing benchmark scoring logic.

## Acceptance

- Focused pytest covers gate manifest validation and failure cases.
- `python -m py_compile` passes for touched Python modules.
- `git diff --check` passes.
