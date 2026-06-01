# task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. task253 exists because task251 closed the HotpotQA loader issue but local
   Qwen packing still fails before `packed_qwen` shards on missing
   `cosmos_xenna`.
2. Packed shards are local prep evidence only; they are not a candidate FT
   checkpoint/export/live eval artifact and do not authorize task243 comparison.
3. If using remote node `NemTron` for debug-only packing checks, code must be
   synced to `/root` first per project rule.
4. AIME2025 prompts and labels remain held-out eval/decontam material only.
5. Base branch for task253 is `origin/main` after #328 merge commit
   `61fa65e9e9a535d531a65072c839760c3488207f`; lead docs source is
   `origin/intern_nemotron_lead/session1-recovery-task-docs`
   `e0a1ebcbdb1976bb39196135f5bcbd8ef5958d0a`.
6. This worker image did not have `uv`; `/usr/bin/python` initially missed
   `cosmos_xenna`, but user-site `pip install cosmos-xenna==0.1.8` made the
   Xenna import pass.
7. Qwen packing also required declared dependency `pydantic-settings`; installing
   `pydantic-settings==2.14.1` cleared that second local dependency blocker.
8. Successful task253 packing output is under
   `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen`;
   metadata reports `num_shards=8`, `total_sequences=1093`,
   `total_tokens=951216`, `pack_size=8192`.
9. Qwen packed SFT chat contract validation passed for the produced
   `packed_qwen/splits` against the Qwen3-4B tokenizer path.
