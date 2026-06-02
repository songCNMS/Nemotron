# task302_qwen_aime_v11_30b_independent_review_runbook_s1 - task knowledge

<!-- METADATA:SESSION=3 -->

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
5. pr-state: As of Session 2, task302 PR #361 is open/base main/CLEAN at exact
   head `1c56762f0a7f19117fbfa1ebbb23db918043dc95`; the earlier `7c36f6eb`
   head was only the first acceptance commit before the PR URL/status follow-up.
6. scope: #361 is initial acceptance/runbook scaffolding only, not a
   substantive task298-task301 evidence approval.
7. session3-visibility: Current upstream heads are task298
   `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`, task299
   `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`, task300
   `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`, and task301/#362
   `b8e42b3e748c8c80cb3c4a938f2db06c9cb0b6d6`.
8. session3-gate: task298 and task300 are acceptance-only in branch docs,
   task299 has preliminary tokenizer parity notes but no final 30B-ready
   root/checksum/decontam report, and task301 is blocked-before-launch with a
   stale visibility section. Keep all gates `REQUEST_CHANGES/HOLD` until exact
   official artifacts, commands/env/logs, checksums, metrics, and residuals are
   available.
