# intern_nemotron_worker_1 - personal knowledge base

<!-- METADATA:SESSION=4 -->

---

## Knowledge entries

1. task246: For manifest files, avoid embedding self-referential sha256 fields;
   write a sibling `.sha256` file for the final-file checksum and verify it
   with direct `sha256sum`.
2. task246: The real V10 decontam artifact set is prompt-only heldout corpus
   plus sparse NuminaMath sidecar input; it is not training/eval/FT evidence.
