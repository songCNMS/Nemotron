# task035_contamination_pipeline_s1 - task_knowledge

<!-- METADATA:SESSION=1 -->

## Session 1 Notes

- `contamination_matrix.py` is a local registry report; it reads YAML via `unified_index.yaml` and performs no HF downloads, live data scans, Docker/SIF smoke, or cluster work.
- The matrix reuses `classify_contamination_row` from `contamination_audit.py`; keep blocker/informational posture aligned with `--check-contamination`.
- `--eval-overlap-matrix` is the canonical CLI flag; `--contamination-matrix` is an alias for operator discoverability.
- Live registry smoke on this branch reported 14 M0 data rows, 0 blockers, 0 informational findings, and 14 clean rows.
