# task303_qwen_aime_v11_30b_task301_salvage_review_s1 - task knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Review target is #362 exact head
   `c75c584875afdbdde4130775cbdc83355e7639ea`.
2. task301 disposition is
   `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`;
   this is not a clean training PASS.
3. `iter_0000035` is the candidate checkpoint. It must be treated as a salvage
   candidate until independent review accepts inventory/checksums and lead
   assigns a later canary gate.
4. Downstream canary, corrected AIME/task243 eval, export, endpoint, promotion,
   and follow-on 30B work remain blocked during this review.
5. worker_4 review decision for #362 head
   `c75c584875afdbdde4130775cbdc83355e7639ea` is
   `APPROVE_SALVAGE_CANDIDATE_FOR_LATER_NON_AIME_CANARY_CONSIDERATION_ONLY`.
6. Remote root was verified via read-only SSH at
   `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`;
   local copied salvage bundle checks also passed.
7. The large 399G checkpoint shard hashes were not fully recomputed during
   review. The review verified the checkpoint file count, size, inventory
   manifest hash, checksum manifest hash, and selected salvage manifest
   checksums. Treat full checkpoint loading as a later canary/runtime gate.
