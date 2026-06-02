# task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1 - task knowledge

<!-- METADATA:SESSION=122 -->

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
16. Session 93: active run remains in progress with remote rank logs/manifests
   present but no rc, summary, completions, parser diagnostics, official report,
   or PR.
17. Session 94: active run remains in progress after more than twelve minutes,
   still without rc/results/report; command timeout is configured for 240
   minutes, so lead did not interrupt.
18. Session 95: active run remains in progress after more than seventeen
   minutes and log progress reached `1/30` with `aime_01_r01` parsed/correct,
   but no final artifacts or official worker report exist yet; gate remains
   HOLD.
19. Session 96: rank event logs show `generation_batch_done` for batch 0 at
   about 832.5s and `generation_batch_start` for `start_index=1`; runner
   finalization should produce per-rank files plus rank0 aggregate summary,
   results, full completions, parser diagnostics, and checksum manifest before
   any gate decision.
20. Session 97: active run still has no rc or final task306 artifacts; rank
   logs remain at batch 1 start, and final-named local files are copied task300
   base inputs rather than task306 outputs.
21. Session 98: active run progressed to `2/30`; batch 1 latency was about
   708s and batch 2 started. No rc, final task306 artifacts, blocker, PR, or
   official worker report exists yet.
22. Session 99: active run progressed to `3/30`; the first three AIME rows are
   parsed/correct in log output, but there is still no rc, final task306
   artifacts, blocker, PR, or official worker report.
23. Session 100: active run remains in progress after about thirty-three minutes
   with latest visible progress still `3/30`; no rc, final artifacts, blocker,
   PR, or official worker report exists.
24. Session 101: active run progressed to `4/30`; batch 3 latency was about
   430.6s and batch 4 started. No rc, final task306 artifacts, blocker, PR, or
   official worker report exists yet.
25. Session 102: active run remains in progress after about forty minutes with
   latest visible progress still `4/30`; no rc, final artifacts, blocker, PR,
   or official worker report exists.
26. Session 103: active run remains in progress after about forty-three minutes
   with latest visible progress still `4/30`; no rc, final artifacts, blocker,
   PR, or official worker report exists.
27. Session 104: active run remains in progress after about forty-six minutes
   with latest visible progress still `4/30`; rank logs still show
   `start_index=4` in progress, with no rc or final artifacts.
28. Session 105: active run remains in progress after about fifty-two minutes
   with latest visible progress still `4/30`; no rc, final artifacts, blocker,
   PR, or official worker report exists.
29. Session 106: active run remains in progress after about fifty-five minutes;
   worker status has no new report, and remote rank event logs for all ranks
   still show `generation_batch_start` at `start_index=4` with no
   `generation_batch_done` for row 5.
30. Session 107: active run remains in progress after about fifty-nine minutes;
   no PR, mailbox report, rc, final FT artifacts, or blocker exists. Latest
   visible progress is still `4/30`.
31. Session 108: active run remains in progress after about sixty minutes;
   latest visible progress is `5/30`, with `aime_05_r01` length-stopped,
   parsed false, and correct false. No final artifacts or official report exist.
32. Session 109: active run remains in progress after about sixty-three
   minutes; latest visible progress is `6/30`, with `aime_06_r01` parsed true
   and correct true. No rc, final artifacts, PR, or official report exists.
33. Session 110: active run remains in progress after about sixty-six minutes;
   latest visible progress is still `6/30`, with no rc, final artifacts, PR, or
   official report.
34. Session 111: active run remains in progress after about seventy minutes;
   latest visible progress is still `6/30`, with no rc, final artifacts, PR, or
   official report.
35. Session 112: active run remains in progress after about seventy-three
   minutes; latest visible progress is still `6/30`, with no rc, final
   artifacts, PR, or official report.
36. Session 113: active run remains in progress after about seventy-six
   minutes; latest visible progress is still `6/30`, with no rc, final
   artifacts, PR, or official report.
37. Session 114: active run remains in progress after about eighty minutes;
   latest visible progress is still `6/30`, with no rc, final artifacts, PR, or
   official report.
38. Session 115: active run remains in progress after about eighty-two minutes;
   latest visible progress is `7/30`, with row 7 parsed true/correct false.
   No rc, final artifacts, PR, or official report exists.
39. Session 116: active run remains in progress after about eighty-five
   minutes; latest visible progress is `8/30`, with row 8 parsed true/correct
   true. No rc, final artifacts, PR, or official report exists.
40. Session 117: active run remains in progress after about ninety-two minutes;
   latest visible progress is still `8/30`. No PR, mailbox report, local/remote
   rc, final FT artifacts, or blocker exists.
41. Session 118: active run remains in progress after about ninety-five
   minutes. Remote rank logs show row 9 generation in progress via
   `generation_batch_start` at `start_index=8` on ranks 0-7, with no
   corresponding done event yet; no final artifacts or official report exist.
42. Session 119: active run remains in progress after about ninety-nine
   minutes. Latest stdout progress remains `8/30`, and remote rank logs still
   show `start_index=8` in progress with no done event. No final artifacts,
   blocker, PR, or official report exists.
43. Session 120: active run remains in progress after about one hundred three
   minutes. Latest stdout progress remains `8/30`, and remote rank logs still
   show `start_index=8` in progress with no done event. No final artifacts,
   blocker, PR, or official report exists.
44. Session 121: active run remains in progress after about one hundred five
   minutes. Latest stdout progress advanced to `9/30`, with row 9 length-
   stopped parsed false/correct false, and rank logs show `start_index=9`
   active. No final artifacts, blocker, PR, or official report exists.
45. Session 122: active run remains in progress after about one hundred eight
   minutes. Latest stdout progress remains `9/30`, and remote rank logs still
   show `start_index=9` in progress with no done event. No final artifacts,
   blocker, PR, or official report exists.
