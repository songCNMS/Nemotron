# task302_qwen_aime_v11_30b_independent_review_runbook_s1 - task knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. review: 30B run acceptance requires independent review of runtime, data,
   training, base score, canary, and corrected AIME FT-vs-base evidence.
2. boundary: Review/runbook does not grant export, endpoint, promotion, or
   release clearance.
3. initial-scan: On acceptance, no task298-task301 PRs or remote heads were
   visible through `gh pr list` or `git ls-remote --heads origin '*task298*'
   '*task299*' '*task300*' '*task301*'`.
4. gate: Missing exact upstream heads/artifacts keeps task302 in HOLD; no 30B
   approve decision can be made from assignment docs alone.
