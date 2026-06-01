# task246_qwen_aime_v10_real_decontam_corpus_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. The task242 placeholder file is intentionally not accepted as a real
   decontamination corpus; task242 local prep must fail closed until a real
   corpus is supplied.
2. AIME25 prompts and labels are heldout eval/decontamination material only;
   training outputs must not include AIME25 labels or answer-supervision rows.
3. `/mnt/cephfs/data/processing/lei.song` is shared storage and existing files
   under it must not be deleted.
4. Task246 branch base is `origin/main`
   `20973e78f196d7e5d71993f60dc74a3500223f5f`, which includes PR #321.
5. The task246 real heldout corpus path is
   `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`;
   it has `560` prompt-only rows, `560` unique prompt hashes, no duplicate
   prompts, and sha256
   `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`.
6. The task246 real V10 M0 sidecar input path is
   `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`;
   fixed NuminaMath-CoT scan found only `8` V10 candidate rows from `859494`
   scanned rows, so task248 should treat the sidecar as real but sparse.
7. Independent validation found `0` AIME25 prompt exact hits in sidecar train
   JSONL and `0` decontam blocker findings against the heldout corpus.
8. The top task246 manifest must not embed a self-referential
   `manifest_sha256`; its final-file checksum is recorded in
   `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json.sha256`.
   The Session 3 final top manifest sha256 is
   `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`.
9. Lead approved PR #325 for self-merge on 2026-06-01 after checksum re-review;
   the task remains data/corpus evidence only, with no accepted training/eval/FT
   judgment.
10. PR #325 merged approved head
    `266b6a14262278b4fe27f75a3273fc156a5538ce` at
    `2026-06-01T17:43:24Z` with merge commit
    `2775dff05948acce3a35a2d941bbd2f96d074b4a`.
