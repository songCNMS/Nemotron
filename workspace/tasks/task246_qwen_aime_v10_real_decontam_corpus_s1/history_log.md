# task246_qwen_aime_v10_real_decontam_corpus_s1 - History Log

<!-- METADATA:SESSION=4 -->

## Session 0 - Assigned

- Created by `intern_nemotron_lead` for `intern_nemotron_worker_1`.
- Purpose: replace task242 placeholder decontamination/input paths with real,
  lead-reviewable heldout corpus and V10 M0/input evidence.
- Initial disposition: Assigned; no training/eval expected from this task.

## Session 1 - 2026-06-01 UTC - Accepted by worker

- Fetched current `origin/main` after PR #321 at
  `20973e78f196d7e5d71993f60dc74a3500223f5f`.
- Fetched lead task-doc branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at `5d5e3fa`.
- Created worker branch
  `intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- Imported task246 README/history/task_knowledge and updated worker status to
  Working.
- Boundaries acknowledged: no training/eval/endpoints, no main push or
  self-merge, no deletion under `/mnt/cephfs/data/processing/lei.song`, and no
  AIME25 labels/prompts in trainable outputs.

## Session 2 - 2026-06-01 UTC - Produced real corpus/input artifacts

- Added `build_task246_artifacts.py` to build a prompt-only heldout
  AIME25/HMMT/MATH corpus from fixed public dataset revisions and a task-owned
  V10 M0 sidecar input from fixed NuminaMath-CoT train shards.
- Produced artifacts under
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- Heldout corpus:
  `heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`, `560` rows,
  `560` unique prompt hashes, sha256
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`.
- V10 M0 sidecar input:
  `m0_v10_math_sidecar`, `859494` NuminaMath rows scanned, `8` V10 candidate
  rows written to train split, `0` val rows, `0` decontam-blocked candidates.
- Independent validation confirmed no heldout label-key leaks, M1 sidecar
  conversion succeeds for the `8` train rows, decontam drops `0` sidecar train
  rows, and exact AIME25 prompt hits in sidecar train JSONL are `0`.
- Did not run training, eval, endpoint launch, main push, self-merge, or shared
  processing deletion.

## Session 3 - 2026-06-01 UTC - Fixed manifest checksum evidence

- Addressed lead REQUEST_CHANGES/HOLD for PR #325: the top manifest previously
  reported the checksum computed before embedding the checksum field, while the
  final file hash was different.
- Updated `build_task246_artifacts.py` so the top manifest does not embed a
  self-referential `manifest_sha256` field and writes the final-file checksum to
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json.sha256`.
- Regenerated task246 artifacts. Direct `sha256sum` of top `manifest.json` and
  the `.sha256` sidecar now both report
  `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`.
- Revalidated heldout rows/hash count, sidecar conversion, decontam drops, and
  exact AIME25 prompt hits. Counts remain `560` heldout rows, `8` sidecar train
  rows, `0` sidecar val rows, `0` decontam drops, and `0` exact AIME25 prompt
  hits in sidecar train JSONL.
- Did not run training, eval, endpoint launch, main push, self-merge, or shared
  processing deletion.

## Session 4 - 2026-06-01 UTC - Lead approval and merge closeout

- Lead approved PR #325 at head
  `266b6a14262278b4fe27f75a3273fc156a5538ce` after independently verifying
  the checksum fix and core artifact evidence.
- Residual risks accepted for this task: sparse `8`-row V10 sidecar input and
  the MATH-500 license note. No training/eval/FT judgment is accepted from this
  task.
- Marked task246 `Completed` and worker status `Idle` on the PR branch before
  self-merge per worker playbook.
- Boundaries remained unchanged: no training, eval, endpoint launch, main push,
  shared processing deletion, or AIME25 trainable prompt/label output.
