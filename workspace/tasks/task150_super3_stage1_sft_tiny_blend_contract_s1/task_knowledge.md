# task150_super3_stage1_sft_tiny_blend_contract_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- Generic Super3 Stage1 SFT core profiles should use Super3-owned blend files
  under `src/nemotron/recipes/super3/stage1_sft/config/data_prep/`.
- Generic Super3 default and tiny profiles should not require `used_in` tags;
  `used_in_filter` should be `null`.
- Arbitrary relative and absolute `blend_path` overrides must remain preserved;
  only checked-in `src/nemotron/recipes/...` defaults are resolved
  repo-relative.
