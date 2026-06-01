# task256_qwen_aime_v10_task255_artifact_review_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. task256 is an independent artifact review task. It must not run AIME eval or
   make a quality judgment.
2. The task255 candidate HF export path is
   `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
3. The global gate remains HOLD until a same-harness FT-vs-base comparison
   proves FT exact-normalized accuracy is at least the accepted base `11/30`.
4. task256 request-changed task255 artifact use because `/root/task255_...`
   checkpoint/export paths were not reviewer-accessible from worker_5, even
   though task255 logs and inventories were internally consistent.
5. #329 should not be approved until worker_2 provides reviewer-accessible
   artifact evidence or a lead-accepted blocker/closeout path.
