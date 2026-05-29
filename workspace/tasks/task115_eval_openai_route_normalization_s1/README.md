# task115_eval_openai_route_normalization_s1

## Scope

- Normalize Stage3 eval default OpenAI-compatible route strings to slashless
  paths:
  - `/v1/chat/completions`
  - `/v1/completions`
- Cover both Super3 and Nano3 defaults because both carried the same trailing
  slash route strings.
- Add focused static tests proving default routes and inherited Super3 basket
  routes stay slashless.

## Boundaries

- No live benchmark or eval run.
- No endpoint call, W&B run, cluster job, deployment, promotion, direct
  `main`/`master` push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task115_eval_openai_route_normalization_s1`
- Base: `d64cbd067a15cca222b9eba200af1eb1ec5b7788`
- PR: https://github.com/songCNMS/Nemotron/pull/221
