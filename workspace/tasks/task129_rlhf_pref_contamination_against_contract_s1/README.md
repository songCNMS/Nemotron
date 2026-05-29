# task129_rlhf_pref_contamination_against_contract_s1 - RLHF pref contamination targets

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Background

M0 data registry rows carry machine-checkable `contamination_against` target
lists and are audited by the registry CLI. RLHF preference-data candidates only
carried prose contamination strings, even when a row was `m0_landed` or marked
`hf_revision_pin_required`.

## Goals

- Add explicit `contamination_against` lists to RLHF preference-data registry
  rows.
- Extend schema validation so landed or revision-pin-required pref rows require
  non-empty `list[str]` contamination targets.
- Extend the contamination audit and CLI path so required pref rows are checked
  offline with the M0 contamination target contract.
- Preserve exploratory pref rows that are neither landed nor pin-required.

## Acceptance Criteria

- [x] Branch starts from `main`
  `22d33bf428bed321c0277badc5d193ada62abf00`.
- [x] RLHF pref rows carry machine-checkable contamination target lists.
- [x] Schema/unified-index validation rejects required pref rows without real
  contamination targets.
- [x] Contamination audit and CLI include landed or pin-required pref rows.
- [x] Focused pytest, contamination CLI, py_compile, Ruff, structured probe,
  and diff whitespace checks pass.
- [ ] PR opened to `main`.

## PR

- Pending.
