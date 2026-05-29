# task129_rlhf_pref_contamination_against_contract_s1 - History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Received PM assignment to enforce `contamination_against` for RLHF pref
  candidates that are landed or require HF revision pins.
- Started from local `main` synced to `origin/main`
  `22d33bf428bed321c0277badc5d193ada62abf00` and created branch
  `intern_nem_dev_2/task129_rlhf_pref_contamination_against_contract_s1`.
- Added `contamination_against` target lists to HelpSteer2, UltraFeedback, and
  distilabel Orca DPO pair pref rows.
- Added pref-row contamination schema validation and wired it through unified
  index validation plus the RLHF pref registry loader.
- Extended the contamination audit to include `m0_landed` or
  `hf_revision_pin_required` pref rows while keeping exploratory pref rows
  skipped.
- Added focused tests and verified the required static/offline checks.
