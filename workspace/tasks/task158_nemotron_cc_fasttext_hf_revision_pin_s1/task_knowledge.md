# task158_nemotron_cc_fasttext_hf_revision_pin_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- FastText HF repo remains `mlfoundations/fasttext-oh-eli5`.
- FastText filename remains
  `openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin`.
- Pinned revision is `cd8b714a90f2dbcd3b02cf5fc972e5d7c7f4f107`.
- Tests must stay static/AST-only and must not perform a live HF download or
  import the Curator/Ray-dependent product module.
- PR #265 merged to `main` at
  `9efec596f0401ab2fbe4909ac54e82be8872ec55` after independent gate and
  merged-main verification.
