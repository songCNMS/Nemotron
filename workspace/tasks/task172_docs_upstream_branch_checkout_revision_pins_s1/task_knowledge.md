# task172_docs_upstream_branch_checkout_revision_pins_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- PM-provided upstream pins:
  - Megatron-Bridge `super-v3`:
    `f570c0529c81b57cb2ae909bd31a19408c7f4583`
  - Megatron-Bridge `nano-v3`:
    `1cedb0a9c5f79d2cd2b5226a86b794b9f0e048a8`
  - NeMo-RL `super-v3`:
    `bb0a7d43931950a74522e159f7117543a87b580b`
  - AutoModel `nemotron-omni`:
    `7dfec6130ddf675cc9721d1619945dcc743f0095`
- This task is docs/static-test only; no live upstream clone/fetch/checkout
  or build/run activity is in scope.
- Closeout: PR #279 merged to `main` at
  `cb04003551bb3277831466deb35b0e9e95f17f3c`; PM merged-main verification
  passed focused upstream checkout revision pytest, `py_compile`, Ruff, diff
  checks, and the structured Markdown/static probe.
