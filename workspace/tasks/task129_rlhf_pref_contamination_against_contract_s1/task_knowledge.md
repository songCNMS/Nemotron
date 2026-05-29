# task129_rlhf_pref_contamination_against_contract_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- RLHF pref rows become operationally relevant for contamination target checks
  when `m0_landed` is true or `hf_revision_pin_required` is true.
- Keep exploratory pref rows without either flag non-blocking so candidate
  discovery can stay lightweight.
- Reuse the M0 `contamination_against` shape: non-empty list of non-empty
  strings, with placeholder-only lists tracked by the contamination audit.
