# task319_qwen_all_sft_raw_blend_decontam_feasibility_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

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
9. PR #383 carries the official task319 report:
   `https://github.com/songCNMS/Nemotron/pull/383`.
10. No materialization or packing is authorized by task319; the report is
    source/decontam feasibility evidence only.
11. Lead gate for task319/#383 accepted
    `APPROVE_FEASIBILITY_DOCS / NO_PACK_OR_TRAIN_RELEASE` at head
    `4775bc17f2792430508eb15aa7669ac2562071f6`; this does not authorize
    materialization, packing, training, eval, export, endpoint, promotion,
    task255 reuse, AIME2025 train data, shared mutation/deletion, main push,
    merge, or self-merge.
12. Await coordinator or authorized non-author merge path before any #383 merge
    action.
13. Session 4 received task322 assignment for raw materialize/count/decontam on
    a separate branch; task319 remains open/unmerged and authorizes no
    additional action.
