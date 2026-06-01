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
5. Remote branch head `be3803fcf1aa7863255d939d34d03f633f95845d` is an
   acceptance/docs/status commit only; it is not packing evidence.
6. Official task253 closeout head
   `749ade2e05b18ae0f1083342eeef0f8a2d61b11e` reports
   `PASS_PACKED_QWEN_LOCAL_ONLY`, but lead acceptance still requires
   independent artifact/repro review.
7. The reported packed artifact uses Qwen tokenizer-native chat template with
   `enable_thinking=false` and `truncate_history_thinking=false`, `num_shards=8`,
   `total_sequences=1093`, and `pack_size=8192`.
8. The local user-site pip dependency workaround is residual risk and should not
   be treated as a production environment prescription.
