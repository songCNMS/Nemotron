# task282_qwen_aime_v11_runbook_provenance_pipeline_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Session 74 authorizes an attempted full pipeline only through sequential
   lead gates.
2. #344/task276 merged packed-data evidence; it does not by itself clear
   training, eval, promotion, or scale.
3. Runbook must preserve no AIME2025 train data, no task255 reuse, no shared
   deletion, and no 30B/8-GPU until explicit future authorization.
4. #344/task276 is merged into main at
   `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` from merged head
   `07efab4fa0d8367e96f54af3d2cdc70768d73595`; it supplies packed-data
   evidence only.
5. Accepted task276 packed root:
   `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
6. Read-only verification for task282 found `packed_qwen_evidence_manifest.json`
   sidecar PASS and all 48 shard checksum entries PASS.
7. The sparse split risk must be carried into task278/task279 and any future
   release decision: valid has 1 packed row and test has 0 rows.
8. Current sequence is task278 no-training config/import preflight, task279
   independent review, lead-processed release decision, bounded Qwen3-4B SFT
   smoke if explicitly released, non-AIME canary, corrected AIME2025 same-harness
   FT-vs-base comparison, and then no promotion/30B unless FT >= base and a
   separate lead gate authorizes it.
