# task249_qwen_aime_v10_live_contam_gate_review_s1 - Task Knowledge

<!-- METADATA:SESSION=5 -->

## Knowledge Entries

1. Static approval of PR #317 through #321 did not approve first go/no-go.
2. Missing base artifacts, missing FT artifacts, or protocol mismatch all keep
   the live gate on HOLD.
3. AIME25/HMMT/MATH heldout contamination is a hard blocker.
4. This task must review live evidence only; missing or indirect runtime
   evidence keeps the first Qwen3-4B gate on HOLD.
5. At Session 4, task246 is visible at
   `a53c913ab80e37197ccfe7525ea04e0ac80c96fe` but has no PR, no
   `real_decontam_corpus_report.md`, and no visible task246 output dir.
6. At Session 4, task247 is visible at
   `94c21c9a8cb229f0357a049a698de898963810f1` and has a local AIME2025
   input/cache bundle with 30 rows and labels stored in the cache, but no
   published `qwen4b_base_smoke_report.md`, no base `summary.json`, no
   `results.jsonl`, no `command.txt`, and no endpoint model manifest.
7. Task247 corrected AIME input/cache availability must be kept separate from
   base readiness: it does not prove a reachable Qwen3-4B endpoint, a base
   score, or same-harness base artifacts.
8. At Session 4, task248 is visible at
   `200741802a9ae9cb9f3e16af8f1b7e66fee69857` and publishes an acceptable
   blocked-before-prep report; this approves the blocker record only, not the
   first go/no-go.
9. At Session 4, task250 PR #324 is OPEN/CLEAN at
   `d1525aa617378e407ffa2e99fde44630f9ab43dc` and correctly keeps NO-GO/HOLD,
   but the live runbook still needs a content refresh for task247 cache
   visibility, task248 branch/report visibility, and task249 PR #323 visibility.
10. At Session 5, PR #324 is OPEN/CLEAN at
    `4fd7978353deb9702e880d2734d8b99bfaf8544b`, but lead sequencing says
    worker_5 is refreshing #324 against #323@`68a8ee77ee25f5dbbac170c935e8487b88198ce2`.
    Keep #323 in-progress/HOLD and only refresh the matrix when the refreshed
    #324 current-head evidence is available.
