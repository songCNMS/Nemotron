# task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1 - task knowledge

<!-- METADATA:SESSION=124 -->

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
46. Session 123: active run remains in progress after about one hundred
   thirteen minutes. Latest stdout progress remains `9/30`, and remote rank
   logs still show `start_index=9` in progress with no done event. No final
   artifacts, blocker, PR, or official report exists.
47. Session 124: active run remains in progress after about one hundred
   seventeen minutes. Latest stdout progress advanced to `10/30`, with row 10
   parsed true/correct false, and rank logs show `start_index=10` active. No
   final artifacts, blocker, PR, or official report exists.
48. Session 125: active run remains in progress after about one hundred
   twenty-four minutes. Latest stdout progress remains `10/30`, and rank logs
   still show `start_index=10` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
49. Session 126: active run remains in progress after about one hundred
   twenty-seven minutes. Latest stdout progress remains `10/30`, and rank logs
   still show `start_index=10` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
50. Session 127: active run remains in progress after about one hundred
   thirty-one minutes. Latest stdout progress remains `10/30`, and rank logs
   still show `start_index=10` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
51. Session 128: active run remains in progress after about one hundred
   thirty-four minutes. Latest stdout progress remains `10/30`, and rank logs
   still show `start_index=10` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
52. Session 129: active run remains in progress after about one hundred
   thirty-six minutes. Latest stdout progress advanced to `11/30`, with row 11
   length-stopped parsed false/correct false, and rank logs show
   `start_index=11` active. No final artifacts, blocker, PR, or official
   report exists.
53. Session 130: active run remains in progress after about one hundred
   thirty-nine minutes. Latest stdout progress remains `11/30`, and rank logs
   still show `start_index=11` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
54. Session 131: active run remains in progress after about one hundred
   forty-three minutes. Latest stdout progress remains `11/30`, and rank logs
   still show `start_index=11` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
55. Session 132: active run remains in progress after about one hundred
   forty-six minutes. Latest stdout progress remains `11/30`, and rank logs
   still show `start_index=11` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
56. Session 133: active run remains in progress after about one hundred fifty
   minutes. Latest stdout progress remains `11/30`, and rank logs still show
   `start_index=11` active with no done event. No final artifacts, blocker, PR,
   or official report exists.
57. Session 134: active run remains in progress after about one hundred
   fifty-three minutes. Latest stdout progress remains `11/30`, and rank logs
   still show `start_index=11` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
58. Session 135: active run remains in progress after about one hundred
   fifty-five minutes. Latest stdout progress advanced to `12/30`, with row 12
   length-stopped parsed false/correct false. No final artifacts, blocker, PR,
   or official report exists.
59. Session 136: active run remains in progress after about one hundred
   fifty-nine minutes. Latest stdout progress remains `12/30`, and rank logs
   show `start_index=12` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
60. Session 137: active run remains in progress after about one hundred
   sixty-one minutes. Latest stdout progress remains `12/30`, and rank logs
   still show `start_index=12` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
61. Session 138: active run remains in progress after about one hundred
   sixty-four minutes. Latest stdout progress remains `12/30`, and rank logs
   still show `start_index=12` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
62. Session 139: active run remains in progress after about one hundred
   sixty-seven minutes. Latest stdout progress remains `12/30`, and rank logs
   still show `start_index=12` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
63. Session 140: active run remains in progress after about one hundred
   seventy minutes. Latest stdout progress remains `12/30`, and rank logs
   still show `start_index=12` active with no done event. No final artifacts,
   blocker, PR, or official report exists.
64. Session 141: active run remains in progress after about one hundred
   seventy-four minutes. Latest stdout progress remains `12/30`, while rank
   logs advanced to `start_index=13` active after completing `start_index=12`.
   No final artifacts, blocker, PR, or official report exists.
65. Session 142: active run remains in progress after about one hundred
   seventy-six minutes. Latest stdout progress advanced to `13/30`, with row
   13 length-stopped parsed false/correct false and row 14 active. No final
   artifacts, blocker, PR, or official report exists.
66. Session 143: active run remains in progress after about one hundred
   seventy-eight minutes. Latest stdout progress remains `13/30`, with row 14
   active. No final artifacts, blocker, PR, or official report exists.
67. Session 144: active run remains in progress after about one hundred
   eighty-one minutes. Latest stdout progress remains `13/30`, with row 14
   active. No final artifacts, blocker, PR, or official report exists.
68. Session 145: active run remains in progress after about one hundred
   eighty-six minutes. Latest stdout progress remains `13/30`, with row 14
   active. No final artifacts, blocker, PR, or official report exists.
69. Session 146: active run remains in progress after about one hundred ninety
   minutes. Latest visible stdout progress remains `13/30`, with row 14 active.
   No final artifacts, blocker, PR, or official report exists.
70. Session 147: active run remains in progress after about one hundred
   ninety-three minutes. Latest visible stdout progress advanced to `14/30`,
   with row 15 active. No final artifacts, blocker, PR, or official report
   exists.
71. Session 148: active run remains in progress after about one hundred
   ninety-seven minutes. Latest visible stdout progress remains `14/30`, with
   row 15 active. No final artifacts, blocker, PR, or official report exists.
72. Session 149: active run remains in progress after about two hundred one
   minutes. Latest visible stdout progress remains `14/30`, with row 15 active.
   No final artifacts, blocker, PR, or official report exists.
73. Session 150: active run remains in progress after about two hundred four
   minutes. Latest visible stdout progress remains `14/30`, with row 15 active.
   No final artifacts, blocker, PR, or official report exists.
74. Session 151: active run remains in progress after about two hundred eight
   minutes. Latest visible stdout progress remains `14/30`, with row 15 active.
   No final artifacts, blocker, PR, or official report exists.
75. Session 152: active run remains in progress after about two hundred twelve
   minutes. Latest visible stdout progress remains `14/30`, with row 15 active.
   No final artifacts, blocker, PR, or official report exists.
76. Session 153: active run remains in progress after about two hundred
   fourteen minutes. Latest visible stdout progress advanced to `15/30`, with
   row 16 active. No final artifacts, blocker, PR, or official report exists.
77. Session 154: active run remains in progress after about two hundred
   twenty-one minutes. Latest visible stdout progress advanced to `17/30`,
   with row 18 active. No final artifacts, blocker, PR, or official report
   exists.
78. Session 155: active run remains in progress after about two hundred
   twenty-four minutes. Latest visible stdout progress remains `17/30`, with
   row 18 still active. No final artifacts, blocker, PR, or official report
   exists.
79. Session 156: active run remains in progress after about two hundred
   twenty-eight minutes. Latest visible stdout progress remains `17/30`, with
   row 18 still active. No final artifacts, blocker, PR, or official report
   exists.
80. Session 157: active run remains in progress after about two hundred
   thirty-two minutes. Latest visible stdout progress remains `17/30`, with
   row 18 still active. No final artifacts, blocker, PR, or official report
   exists.
81. Session 158: active run remains in progress after about two hundred
   thirty-six minutes. Latest visible stdout progress remains `17/30`, with
   row 18 still active. Only task300 base input artifacts are visible; no
   task306 FT final artifacts, blocker, PR, or official report exists.
82. Session 159: active run remains in progress after about two hundred
   thirty-seven minutes. Latest visible stdout progress advanced to `18/30`,
   with row 19 active. No task306 FT final artifacts, blocker, PR, or official
   report exists.
83. Session 160: active run remains in progress after about two hundred
   forty-one minutes. Latest visible stdout progress advanced to `19/30`, with
   row 20 active. No task306 FT final artifacts, blocker, PR, or official
   report exists.
84. Session 161: active run remains in progress after about two hundred
   forty-five minutes. Latest visible stdout progress remains `19/30`, with
   row 20 still active. No task306 FT final artifacts, blocker, PR, or official
   report exists.
85. Session 162: active run remains in progress after about two hundred fifty
   minutes. Latest visible stdout progress remains `19/30`, with row 20 still
   active. No task306 FT final artifacts, blocker, PR, or official report
   exists.
86. Session 163: active run remains in progress after about two hundred
   fifty-six minutes. Latest visible stdout progress remains `19/30`, with row
   20 still active. No task306 FT final artifacts, blocker, PR, or official
   report exists.
87. Session 164: active run remains in progress after about two hundred sixty
   minutes. Latest visible stdout progress advanced to `20/30`, with row 21
   active. No task306 FT final artifacts, blocker, PR, or official report
   exists.
88. Session 165: active run remains in progress after about two hundred
   sixty-two minutes. Latest visible stdout progress remains `20/30`, with row
   21 still active. No task306 FT final artifacts, blocker, PR, or official
   report exists.
89. Session 166: active run remains in progress after about two hundred
   sixty-five minutes. Latest visible stdout progress remains `20/30`, with
   row 21 still active. No task306 FT final artifacts, blocker, PR, or
   official report exists.
90. Session 167: active run remains in progress after about two hundred
   sixty-eight minutes. Latest visible stdout progress remains `20/30`, with
   row 21 still active. Only task300 base input result files are visible; no
   task306 FT final artifacts, blocker, PR, or official report exists.
91. Session 168: active run remains in progress after about two hundred
   seventy minutes. Latest visible stdout progress advanced to `21/30`, with
   row 22 active. Only task300 base input result files are visible; no task306
   FT final artifacts, blocker, PR, or official report exists.
92. Session 169: active run remains in progress after about two hundred
   seventy-three minutes. Latest visible stdout progress remains `21/30`, with
   row 22 still active. No task306 FT final artifacts, blocker, PR, or
   official report exists.
93. Session 170: active run remains in progress after about two hundred
   seventy-six minutes. Latest visible stdout progress advanced to `22/30`,
   with row 23 active. No task306 FT final artifacts, blocker, PR, or official
   report exists.
94. Session 171: active run remains in progress after about two hundred
   eighty-two minutes. Latest visible stdout progress still `22/30`, with row
   23 active. No task306 FT final artifacts, blocker, PR, or official report
   exists.
95. Session 172: active run remains in progress after about two hundred
   eighty-five minutes. Latest visible stdout progress still `22/30`, with row
   23 active. No task306 FT final artifacts, blocker, PR, or official report
   exists. `start_index=22` is about ten minutes old at this check, so this is
   not yet hang evidence.
96. Session 173: active run remains in progress after about two hundred
   ninety minutes. Latest visible stdout progress still `22/30`, with row 23
   active. No task306 FT final artifacts, blocker, PR, or official report
   exists. `start_index=22` is about thirteen minutes old at this check, so
   this is not yet hang evidence.
97. Session 174: active run remains in progress after about two hundred
   ninety-three minutes. Latest visible stdout progress still `22/30`, with
   row 23 active. No task306 FT final artifacts, blocker, PR, or official
   report exists. `start_index=22` is about seventeen minutes old at this
   check, still near the observed long-row range and not yet hang evidence.
98. Session 175: follow-up check superseded Session 174 progress. Active run
   remains in progress after about two hundred ninety-five minutes. Latest
   visible stdout progress advanced to `23/30`, with row 24/start_index23
   active. No task306 FT final artifacts, blocker, PR, or official report
   exists.
99. Session 176: active run remains in progress after about two hundred
   ninety-nine minutes. Latest visible stdout progress remains `23/30`, with
   row24/start_index23 active about five minutes. No task306 FT final
   artifacts, blocker, PR, or official report exists.
100. Session 177: active run remains in progress after about three hundred
   three minutes. Latest visible stdout progress remains `23/30`, with
   row24/start_index23 active about nine minutes. No task306 FT final
   artifacts, blocker, PR, or official report exists.
101. Session 178: follow-up check superseded Session 177 progress. Active run
   remains in progress after about three hundred five minutes. Latest visible
   stdout progress advanced to `24/30`, with row25/start_index24 active. No
   task306 FT final artifacts, blocker, PR, or official report exists.
102. Session 187: active run remains in progress after about three hundred
   thirty-eight minutes. Latest visible stdout progress remains `25/30`, with
   row26/start_index25 active about fifteen minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
103. Session 188: active run remains in progress after about three hundred
   forty-four minutes. Latest visible stdout progress advanced to `26/30`, with
   row27/start_index26 active about one minute. No task306 FT final artifacts,
   blocker, PR, local/remote rc, mailbox report, or official report exists;
   gate remains HOLD pending final same-harness artifacts.
104. Session 189: active run remains in progress after about three hundred
   forty-seven minutes. Latest visible stdout progress remains `26/30`, with
   row27/start_index26 active about three minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
105. Session 190: active run remains in progress after about three hundred
   fifty-one minutes. Latest visible stdout progress remains `26/30`, with
   row27/start_index26 active about eight minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
106. Session 191: active run remains in progress after about three hundred
   fifty-four minutes. Latest visible stdout progress remains `26/30`, with
   row27/start_index26 active about eleven minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
107. Session 192: active run remains in progress after about three hundred
   fifty-eight minutes. Latest visible stdout progress remains `26/30`, with
   row27/start_index26 active about fifteen minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
108. Session 193: active run remains in progress after about three hundred
   sixty-two minutes. Latest visible stdout progress advanced to `27/30`, with
   row28/start_index27 just started. No task306 FT final artifacts, blocker,
   PR, local/remote rc, mailbox report, or official report exists; gate remains
   HOLD pending final same-harness artifacts.
109. Session 194: active run remains in progress after about three hundred
   sixty-five minutes. Latest visible stdout progress remains `27/30`, with
   row28/start_index27 active about four minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
110. Session 195: active run remains in progress after about three hundred
   seventy-three minutes. Latest visible stdout progress remains `27/30`, with
   row28/start_index27 active about ten minutes. Remote artifacts contain rank
   event logs and manifests only, while aggregate result files are still only
   task300 base input artifacts. No task306 FT final artifacts, blocker, PR,
   local/remote rc, mailbox report, or official report exists; gate remains
   HOLD pending final same-harness artifacts.
111. Session 196: active run remains in progress after about three hundred
   seventy-eight minutes. Latest visible stdout progress remains `27/30`, with
   row28/start_index27 active about sixteen minutes. Remote rc is absent,
   worker-owned eval processes remain active, and no task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
112. Session 197: active run remains in progress after about three hundred
   eighty-three minutes. Latest visible stdout progress advanced to `28/30`,
   with row29/start_index28 active after all ranks completed `start_index=27`.
   Partial visible count is `14/28` correct, not final gate evidence. No
   task306 FT final artifacts, blocker, PR, local/remote rc, mailbox report, or
   official report exists; gate remains HOLD pending final same-harness
   artifacts.
113. Session 198: active run remains in progress after about three hundred
   eighty-seven minutes. Latest visible stdout progress remains `28/30`, with
   row29/start_index28 active about five minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
114. Session 199: active run remains in progress after about three hundred
   ninety-one minutes. Latest visible stdout progress remains `28/30`, with
   row29/start_index28 active about ten minutes. No task306 FT final artifacts,
   blocker, PR, local/remote rc, mailbox report, or official report exists;
   gate remains HOLD pending final same-harness artifacts.
115. Session 200: active run remains in progress after about three hundred
   ninety-six minutes. Latest visible stdout progress remains `28/30`, with
   row29/start_index28 active about fourteen minutes. No task306 FT final
   artifacts, blocker, PR, local/remote rc, mailbox report, or official report
   exists; gate remains HOLD pending final same-harness artifacts.
116. Session 201: active run remains in progress after about four hundred two
   minutes. Latest visible stdout progress advanced to `29/30`, with
   row30/start_index29 active after all ranks completed `start_index=28`.
   Partial visible count is `14/29` correct, not final gate evidence. No
   task306 FT final artifacts, blocker, PR, local/remote rc, mailbox report, or
   official report exists; gate remains HOLD pending final same-harness
   artifacts.
117. Session 202: active run remains in progress after about four hundred seven
   minutes. Latest visible stdout progress remains `29/30`, with
   row30/start_index29 active about six minutes. No task306 FT final artifacts,
   blocker, PR, local/remote rc, mailbox report, or official report exists;
   gate remains HOLD pending final same-harness artifacts.
118. Session 203: final artifacts appeared and `remote_no_export_aime_eval.rc=0`.
   Corrected AIME2025 comparison is FAIL: FT `14/30 = 0.4666666666666667`
   versus accepted base `15/30 = 0.5`, delta `-1`. FT results/parser/full
   completions are complete at `30` rows each. Boundary confirmations are true
   for no AIME train data, no task255, no task306 training, no export/endpoint,
   no promotion, no shared deletion, and no main push/merge. Lead assigned
   task307 to worker_4 for independent review/runbook closeout and retained
   FAIL/HOLD pending that review plus worker_3 official closeout reconciliation.
119. Session 204: worker_3 official task306 PR #369 is now visible: OPEN/base
   `main`/CLEAN at head `1255f2356cb014cd1adbe58c7af297f291b222f3`.
   Preliminary lead diff from eval source head `894e2e7` to PR head `1255f235`
   is status/task306 docs/report closeout only, and diff-check passes. Task307
   review target was refreshed to exact PR #369 head plus eval source head.
120. Session 205: worker_3 mailbox closeout and addendum were reconciled.
   Current #369 head is `8201b3943db2d6ed4427c42518736c41f77d67bd`; diff
   `1255f235..8201b394` is metadata/status-only with unchanged FAIL metrics.
   Task307 now reviews exact #369 head `8201b394`; #369 remains unapproved
   pending independent review.
