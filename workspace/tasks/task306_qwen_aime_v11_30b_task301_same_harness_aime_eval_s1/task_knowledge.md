# task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1 - task knowledge

<!-- METADATA:SESSION=92 -->

## Knowledge Entries

1. Accepted 30B base comparator is task300: Qwen3-30B-A3B corrected AIME2025
   score `15/30 = 0.5`.
2. task300 base artifact root:
   `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`.
3. Candidate FT checkpoint is task301 salvage checkpoint
   `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
4. task301 is not a clean training PASS: it reached `35/35`, saved the
   checkpoint, skipped `0`, NaN `0`, then built-in validation hung and
   `train_rc=1`.
5. task304/task305 accepted only a synthetic non-AIME checkpoint-load/completion
   canary with residuals. They are not corrected AIME evidence and do not
   authorize promotion/export/endpoint/additional training.
6. task306 PASS requires FT exact-normalized corrected AIME2025 score
   `>= 15/30` under the same corrected protocol as task300.
7. AIME2025 prompts and labels are held-out eval/decontam inputs only and must
   not enter trainable data.
8. If task306 cannot prove prompt/cache/generation/parser/normalizer/denominator
   equivalence to task300, it must report HOLD or a justified no-training base
   rerun instead of judging the FT checkpoint.
9. Lead branch task docs were pushed at
   `a9c380e9d2fe4577d89c2e013cc86d67c0479365`, and the task306 assignment
   peer_send to `intern_nemotron_worker_3` was delivered.
10. Worker_3 acceptance branch is visible at
   `2ef5515ed81bbf35712e57b2c91cfcc1726f46b5`; branch diff is acceptance docs/
   status only and no task306 PR/output/mailbox completion report is visible
   yet.
11. Session 90 follow-up: task306 remains without PR, official report, output
   root, or active process; an untracked worker-local runner script exists but
   is not evidence until pushed/reported.
12. Lead sent a queued `next` peer_send asking worker_3 for official task306
   artifacts/report or exact blocker.
13. Session 91 confirms no new official task306 evidence: branch unchanged at
   `2ef5515e`, no PR, no mailbox report, no output root, and no active process.
14. Session 92 current state supersedes entry 13: branch is now
   `894e2e71e72f09926128e37f22000802804522bc` with task-owned no-export AIME
   runner and active worker-launched NemTron run under
   `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
15. No task306 rc, summary, full completions, parser diagnostics, official
   report, or PR exists yet; active run observation is not a gate decision.
