# task319_qwen_all_sft_raw_blend_decontam_feasibility_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Task309 accepted only constrained task299/V11 packed data; generic raw
   `stage1_sft/data_blend_raw` remains excluded.
2. Future all-SFT data repair requires source row counts, checksums,
   supervised-token feasibility, and decontam proof before packing.
3. AIME2025 prompts/labels remain held-out eval/decontam only.
4. This task does not authorize final packing or training.
5. Task319 disposition is `PASS_FEASIBILITY_PLAN`: current evidence gives a
   concrete follow-up materialization/decontam route, but raw blend sources are
   not packing-ready now.
6. Source matrix artifact:
   `/work-agents/intern_nemotron_worker_2/outputs/task319_qwen_all_sft_raw_blend_decontam_feasibility_s1/run_20260603T194128Z/matrices/source_matrix.tsv`.
7. Current raw blend has 12 HF entries. Task308 supplies repo revisions and
   file sha256 for all 12, but exact local row counts and supervised-token
   counts are available for 0/12.
8. Follow-up packing should remain blocked until a lead-gated task materializes
   the 12 source files, pins splits/file paths, emits local checksums and row
   manifests, runs heldout/decontam scans, and then produces Qwen tokenizer
   supervised-token counts.
