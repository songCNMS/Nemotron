# task308_qwen_all_sft_pipeline_inventory_audit_s1 - Task Knowledge

<!-- METADATA:SESSION=85 -->

## Knowledge Entries

1. AIME2025 prompts and labels are held-out eval/decontam material only and
   must be excluded from all trainable SFT inventories.
2. The next all-SFT pipeline cannot start training from task301/task306 evidence
   because the prior 30B FT scored `14/30` below the accepted 30B base `15/30`.
3. The inventory must include `stage1_sft` `data_blend_raw`, task276/task299
   packed-data evidence, M1 agentic/math sidecars, and any other eligible SFT
   source before task309 can produce a final all-SFT packed contract.
