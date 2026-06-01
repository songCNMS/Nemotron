# task264_qwen_aime_v11_eval_gate_canary_retention_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Accepted Qwen3-4B base score is `11/30` exact-normalized under the corrected
   same-harness AIME25 `30x1` protocol.
2. task260 found task255 FT had `0/30` parsed and mixed-script/code-token tails
   on all rows, so future artifacts need a non-AIME canary before AIME eval.
3. Existing task257 artifacts retained only `response_tail`; V11 should retain
   full completions or a deterministic debug transcript for forensic review.
4. This task cannot run live AIME eval or authorize promotion/30B.
5. A V11 canary must use synthetic non-AIME prompts only and should be
   documented with prompt-source hashes so reviewers can verify it is not
   train or held-out AIME data.
6. The task264 canary prompt set is
   `qwen_v11_non_aime_export_load_canary_v1`, five synthetic prompts, sha256
   `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`.
7. Future V11 AIME artifacts must retain `full_completions.jsonl` and
   `completion_retention_manifest.json` with response text hashes/references;
   these artifacts are review-only and not trainable data.
8. The first pytest attempt without `PYTHONPATH=src` cannot import `nemotron`;
   the focused test command for this repo is `PYTHONPATH=src pytest -q
   tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py`.
