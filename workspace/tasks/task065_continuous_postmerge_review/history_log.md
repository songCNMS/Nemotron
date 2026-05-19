# history_log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-19 - intern_nemontron_code_reading

- Created this continuous follow-up task from user request: continue review until all new PRs are reviewed.
- Scope selected: PR #73 through PR #85 on current `main`, excluding this review stream's own PRs #86 through #90.
- Branch: `intern_nemontron_code_reading/task065_continuous_postmerge_review`.
- GitHub check: no open PRs; latest merged PR on main is #90. Review scope remains PR #73-#85.
- PR #73/#75/#77/#79/#81/#83/#85 closeout status-only PRs reviewed against current `workspace/interns/intern_nemontron_review_cc/status.md`; PR #89 already fixed the stale Idle `TASK` metadata, no new status bug found.
- PR #74/#76 promotion gate and gap analysis reviewed; focused tests pass in the combined validation set.
- PR #78 RLVR1 smoke wiring reviewed; focused tests pass. Found stale task history metadata in task014 and fixed `METADATA:SESSION=2`.
- PR #80 SWE1 pivot data reviewed. Found real-schema blockers:
  - `m0_swe_pivot_tool_call` used `hf_revision: TBD`, which the existing revision audit incorrectly treated as pinned.
  - `SWE-Gym/SWE-Gym-Lite` currently has only `train` split and patch fields, not `validation` split or `messages` trajectories.
  - Fixed registry revision/split, added patch-only `view_file` pivot fallback, and added tests.
- PR #82 SWE2 OpenHands trace and sandbox watchdog reviewed. Found same SWE-Gym real-schema blocker for SWE2; fixed registry revision/split and added patch-only synthetic read-then-submit trajectory fallback. Watchdog tests pass. Fixed task017 history metadata to `SESSION=5`.
- PR #84 HelpSteer-2 preference converter reviewed. Found `nvidia/HelpSteer2` default config is scalar response-rating rows, not `response_a`/`response_b` pair rows. Added streaming pair adapter for adjacent same-prompt scalar rows, pinned revision, updated registry fields, and added tests. Fixed task018 history metadata to `SESSION=2`.
- Additional metadata fix: task016 history metadata now matches latest `Session 2`.
- Validation:
  - `pytest -q tests/recipes/super3/test_swe_gym_lite_pivot.py tests/recipes/super3/test_swe2_openhands_trace.py tests/recipes/super3/test_helpsteer2_pref.py tests/recipes/super3/test_revision_audit.py tests/recipes/super3/test_m0_data_env.py::test_registries_are_consistent` → 95 passed.
  - `python scripts/validate_data_registries.py --check-revision-pins` → zero blockers, three informational pref candidates.
  - Real HF streaming smoke for `m0_swe_pivot_tool_call`, `m0_swe2_openhands_trace`, `m0_helpsteer2_pref` with 2/1 train/val each → success, no manifest errors.
  - Combined PR-scope tests: promotion gate, gap analysis, RLVR1 smoke wiring, SWE1/SWE2 bridges, sandbox watchdog, unified registry, M0 data env, SWE converters, HelpSteer-2 converter, revision audit → 249 passed, 2 skipped.
- Follow-up PR opened: https://github.com/songCNMS/Nemotron/pull/91
