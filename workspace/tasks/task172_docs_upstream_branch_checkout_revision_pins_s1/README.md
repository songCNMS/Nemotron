# task172_docs_upstream_branch_checkout_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Pin scoped Super3, Nano3, and Nano-Omni AutoModel documentation examples that
clone or checkout upstream release branches to PM-verified exact commit SHAs.

## Scope

- `docs/nemotron/super3/pretrain.md`
- `docs/nemotron/super3/sft.md`
- `docs/nemotron/super3/quantization.md`
- `docs/nemotron/super3/rl/index.md`
- `docs/nemotron/nano3/pretrain.md`
- `docs/nemotron/nano3/sft.md`
- `usage-cookbook/Nemotron-3-Nano-Omni/automodel/automodel_training_cookbook.md`
- Focused static docs test under `tests/docs/`

## Acceptance

- Super3 Megatron-Bridge docs use
  `f570c0529c81b57cb2ae909bd31a19408c7f4583` for `super-v3`.
- Nano3 Megatron-Bridge docs use
  `1cedb0a9c5f79d2cd2b5226a86b794b9f0e048a8` for `nano-v3`.
- Super3 RL docs use
  `bb0a7d43931950a74522e159f7117543a87b580b` for NeMo-RL `super-v3`.
- AutoModel cookbook uses
  `7dfec6130ddf675cc9721d1619945dcc743f0095` for `nemotron-omni`.
- Static tests prove scoped docs keep repo/branch context and exact SHA
  checkout guidance.

## Boundaries

- Docs/static-test only.
- No live git clone/fetch/checkout, build, data prep, train/eval, endpoint
  calls, W&B, cluster jobs, deploy, artifact ops, direct `main`/`master` push,
  or self-merge.
