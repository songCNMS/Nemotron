# task115_eval_openai_route_normalization_s1 knowledge

<!-- METADATA:SESSION=17 -->

## Working Notes

- Super3 and Nano3 Stage3 eval defaults now use slashless OpenAI route paths:
  `/v1/chat/completions` and `/v1/completions`.
- Super3 `m1_basket`, `m1_full_basket`, and
  `m1_full_basket_launcher_available` inherit `default.yaml`; the focused
  loader test asserts the resolved launcher configs keep those inherited routes
  slashless.
- Session 17 added no new task115 implementation knowledge. The follow-up
  task117 enforces the same slashless route contract in the Qwen eval repro
  gate's intended eval path.
