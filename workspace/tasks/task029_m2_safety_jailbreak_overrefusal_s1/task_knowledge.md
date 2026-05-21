# task029_m2_safety_jailbreak_overrefusal_s1 - task_knowledge

<!-- METADATA:SESSION=1 -->

## Session 1 Notes

- Safety, jailbreak, and over-refusal rows are sandbox scaffolds in the M0/M2 registry layer; keep production judge and benchmark-source decisions separate from schema tests.
- `safety_judge_stub` is a deterministic CI scaffold, not a production judge model.
- Prepare and baseline paths should remain sandbox-runnable for this task family; no live HF scans, SIF/Docker smoke, or cluster jobs are required for Session 1 style changes.
- PR #136 was squash-merged before task035 began, so future task029 edits should start from current `main`.
