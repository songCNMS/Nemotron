# task256_qwen_aime_v10_task255_artifact_review_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. task256 is an independent artifact review task. It must not run AIME eval or
   make a quality judgment.
2. The task255 candidate HF export path is
   `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
3. The global gate remains HOLD until a same-harness FT-vs-base comparison
   proves FT exact-normalized accuracy is at least the accepted base `11/30`.
4. Session 2 target head: review task255 PR #329 head
   `d62036e405edc5daa322c09bb89da19b176bb7bf`; prior artifact closeout head
   `dfee98a028a55c00dc2579bef602ee914e88a325` differs only by worker status
   PR-number bookkeeping.
5. task256 acceptance branch is
   `intern_nemotron_worker_5/task256_qwen_aime_v10_task255_artifact_review_s1`;
   findings should be sent by mailbox and no PR is needed unless lead asks.
