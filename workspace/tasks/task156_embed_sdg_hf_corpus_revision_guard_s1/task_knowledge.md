# task156_embed_sdg_hf_corpus_revision_guard_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- Valid Embed Stage0 SDG Hugging Face corpus URIs must use
  `hf://org/dataset@<40-char-lowercase-commit-sha>[/subdir]`.
- Local path `corpus_dir` values remain resolved with `Path(...).resolve()` and
  do not touch Hugging Face download logic.
