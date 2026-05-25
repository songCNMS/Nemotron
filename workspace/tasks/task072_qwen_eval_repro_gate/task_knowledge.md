# task072_qwen_eval_repro_gate - Task Knowledge

<!-- METADATA:SESSION=7 -->

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
5. Session 6 requires raw artifact evidence to be either an existing local path
   or a deliberately checked remote reference such as `vm4vpn:`; missing local
   paths are a gate failure.
6. `/work-agents/endpoints.txt` can list reachable endpoint surfaces without
   Qwen. Record only sanitized counts/model-hit summaries, not credentials.
7. Session 7 added no new gate logic; it recorded PR #173 merge closeout and
   latest-main sync to `ab1fbbf64f892abda34582a7cfc18229fb6f1824`.
