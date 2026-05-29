# task129_rlhf_pref_contamination_against_contract_s1 knowledge

<!-- METADATA:SESSION=3 -->

## Working Notes

- RLHF pref rows become operationally relevant for contamination target checks
  when `m0_landed` is true or `hf_revision_pin_required` is true.
- Keep exploratory pref rows without either flag non-blocking so candidate
  discovery can stay lightweight.
- Reuse the M0 `contamination_against` shape: non-empty list of non-empty
  strings, with placeholder-only lists tracked by the contamination audit.
- PM replacement gate can validate the same head against a newer base before
  independent testing; keep the branch stable unless PM requests a rebase or
  fix.
- After PR #236 merge, fast-forward local `main` to the PM-reported merge
  commit before accepting more work, then record closeout on an owned branch.
