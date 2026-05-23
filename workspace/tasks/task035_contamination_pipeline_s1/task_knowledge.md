# task035_contamination_pipeline_s1 - task_knowledge

<!-- METADATA:SESSION=2 -->

## Session 1 Notes

- `contamination_matrix.py` is a local registry report; it reads YAML via `unified_index.yaml` and performs no HF downloads, live data scans, Docker/SIF smoke, or cluster work.
- The matrix reuses `classify_contamination_row` from `contamination_audit.py`; keep blocker/informational posture aligned with `--check-contamination`.
- `--eval-overlap-matrix` is the canonical CLI flag; `--contamination-matrix` is an alias for operator discoverability.
- Live registry smoke on this branch reported 14 M0 data rows, 0 blockers, 0 informational findings, and 14 clean rows.
- The 2026-05-21 Session 2 note was post-merge sync only; the
  2026-05-23 Session 2 assignment adds local prompt-corpus scanning.
- Prompt-corpus scanning should stay fixture/local-file based and
  should not require live HF full downloads, external APIs, Docker,
  cluster jobs, or W&B.
- Deterministic token n-gram overlap is enough for sandbox posture
  classification when it emits JSON/Markdown-friendly findings.
