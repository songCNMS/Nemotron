# task251_qwen_aime_v10_hotpotqa_loader_unblock_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. #327 merged task248 as a blocked prep report, not as a Qwen3-4B go/no-go
   pass.
2. The current task248 blocker is `hotpotqa/hotpot_qa` under Hugging Face
   `datasets`, where `trust_remote_code` is no longer supported.
3. The smallest expected workaround is a task-owned standard-format HotpotQA
   cache or registry override, with source revision, rows, checksums, and split
   mapping recorded.
4. task251 must not introduce AIME2025 prompts or labels into trainable data;
   AIME2025 remains held out for eval/decontamination only.
5. Passing task251 local prep does not itself authorize task243 comparison,
   FT promotion, or 30B/8-GPU scale.
6. Branch base for task251 is `origin/main`
   `419c8b9fe6415d13ba48c5130a9ecf5e816ceb8e`; lead docs source is
   `origin/intern_nemotron_lead/session1-recovery-task-docs`
   `3c9ce4433479b73d98c517e8fecb2ced26124fb8`.
7. Pinned HotpotQA revision
   `1908d6afbbead072334abe2965f91bd2709910ab` contains standard Parquet files
   under `distractor/`, so task251 can avoid the unsupported loader-script path
   by converting those Parquet shards to task-owned JSONL cache files.
8. `prepare_m0_assets.py` can now read registry-provided `local_jsonl_files`
   before importing or invoking Hugging Face `datasets.load_dataset`, which
   keeps the workaround independent of `trust_remote_code`.
9. task251 local evidence clears the HotpotQA blocker: HotpotQA-only M0 probe
   produced `100` train / `25` validation rows with no errors, and the broader
   task248 M0 selection moved past HotpotQA.
10. The current next local blocker is environment-only for Qwen packing:
    `stage1_sft/data_prep.py` imports `cosmos_xenna`, which is missing from the
    local Python environment. No packed Qwen shards, checkpoints, exports, or
    FT eval artifacts exist.
11. M1 prep with task246 heldout decontamination and sparse sidecar knobs
    `8` train / `0` val shadow produced `1100` train rows, `273` val shadow
    rows, and `0` errors; `agentic_sft_v0_math_heldout_eval.jsonl` has `0`
    rows.
