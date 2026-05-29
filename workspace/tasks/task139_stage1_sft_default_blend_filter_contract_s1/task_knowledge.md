# task139_stage1_sft_default_blend_filter_contract_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- The generic Super3 stage1 SFT default profile should use the Super3-owned
  blend beside the profile.
- `used_in_filter` should be `null` for the generic default unless a
  Super3-owned tag contract is enforced by the blend data.
- `_matches_used_in_filter(None, "nano_v3")` returns false, so a stale filter
  can silently drop records that do not carry `used_in`.
