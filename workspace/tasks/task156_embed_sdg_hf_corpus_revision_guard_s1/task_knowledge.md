# task156_embed_sdg_hf_corpus_revision_guard_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- Valid Embed Stage0 SDG Hugging Face corpus URIs must use
  `hf://org/dataset@<40-char-lowercase-commit-sha>[/subdir]`.
- Local path `corpus_dir` values remain resolved with `Path(...).resolve()` and
  do not touch Hugging Face download logic.
- PR #263 merged to `main` at
  `0b31358436c38e698c7c2bc3a89871df273df21c`; no follow-up task is active.
