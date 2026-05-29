# task160_omni3_valor32k_qa_zip_revision_pin_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Accepted PM assignment and created branch
  `intern_nem_dev_2/task160_omni3_valor32k_qa_zip_revision_pin_s1` from
  `origin/main` at `9efec596f0401ab2fbe4909ac54e82be8872ec55`.
- Added `VALOR32K_QA_ZIP_REVISION` with PM-provided SHA
  `a1eeb58e16fbe84f43a3886fd72fe61fd208b7b2`.
- Changed the default Valor32k QA ZIP URL away from floating
  `refs/heads/main` to the exact commit URL.
- Preserved operator `qa_zip_url` overrides and recorded effective
  `cfg.qa_zip_url` in both artifact source lineage and staging manifest
  metadata.
- Added focused static/AST tests that do not perform a live URL download.
