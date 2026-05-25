# task072_qwen_eval_repro_gate - Task Knowledge

<!-- METADATA:SESSION=5 -->

> Keep only durable cross-session facts that are not obvious from a quick diff.

## Knowledge Entries

1. For the current Qwen target, Super3 chat-template consistency is necessary
   but not sufficient. Gate evidence must name the Qwen checkpoint/tokenizer
   and show the intended `/v1/chat/completions` path.
2. Existing task071 Qwen-30B original records show legacy MMLU-Pro was
   completions-only, short-generation capped, and parser-misaligned; it must
   not count as valid Qwen-chat reproduction.
3. Existing task071 math records show old AIME25/HMMT scores were mixed with
   generation-budget and parser/final-answer failures; corrected Qwen evidence
   needs explicit max-token and final-answer parser contracts.
4. Session 5 added no new gate logic; it recorded the PR-status durable entry
   required by the stop hook.
