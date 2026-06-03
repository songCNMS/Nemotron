# task308_qwen_all_sft_pipeline_inventory_audit_s1 - Task Knowledge

<!-- METADATA:SESSION=89 -->

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
7. Lead HOLD after task308 receipt: do not self-merge #374 until lead gate
   after task312 independent review; no packing/training/eval/export/endpoint
   is authorized.
8. Lead accepted head `b798fdfcfc3144111dd0a6e0f80505df031bcc5e` as
   metadata-only drift; task312 must refresh review over current heads before
   any #374 self-merge gate.
9. PR #374 was lead-approved at exact head
   `a238cacb1f28fb96df58d3a10641a2b7325f61b7` and self-merged at
   `2026-06-03T15:28:23Z`; merge commit
   `eb05e6b324c3159b01070cb575c2be363e773cac`.
