# task155_omni3_valor32k_config_comment_portability_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- Scope is comments/static test only for
  `src/nemotron/recipes/omni3/stage0_sft/config/valor32k.yaml`.
- Runtime dataset default must remain
  `${oc.env:OMNI3_VALOR32K_ENERGON_PATH,/datasets/valor32k/energon}`.
- The removed named-user path fragment is `users/chcui`; scoped guard also
  rejects `/lustre/fs1/portfolios/coreai/`.
