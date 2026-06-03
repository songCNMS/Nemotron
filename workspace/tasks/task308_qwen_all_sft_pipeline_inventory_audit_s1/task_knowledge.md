# task308_qwen_all_sft_pipeline_inventory_audit_s1 - Task Knowledge

<!-- METADATA:SESSION=86 -->

## Knowledge Entries

1. AIME2025 prompts and labels are held-out eval/decontam material only and
   must be excluded from all trainable SFT inventories.
2. The next all-SFT pipeline cannot start training from task301/task306 evidence
   because the prior 30B FT scored `14/30` below the accepted 30B base `15/30`.
3. The inventory must include `stage1_sft` `data_blend_raw`, task276/task299
   packed-data evidence, M1 agentic/math sidecars, and any other eligible SFT
   source before task309 can produce a final all-SFT packed contract.
4. Task308 result: current-main generic `stage1_sft/data_blend_raw` has repo
   and file checksums but no exact row counts or heldout/AIME decontam proof in
   current evidence, so task309 must materialize/count/scan it before including
   it in all-SFT packing.
5. Task308 checksum-backed seed for task309 is the task299 30B-ready V11
   packed root plus task262/task276/task246 decontam evidence; task253 and
   task255 remain excluded.
6. PR #374 carries the task308 report:
   `https://github.com/songCNMS/Nemotron/pull/374`.
