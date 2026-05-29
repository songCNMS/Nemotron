# task147_omni3_text_rl_blend_path_cwd_independence_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- `src/nemotron/kit/train_script.py` was intentionally untouched because PR
  #252 owns the shared resolver surface.
- The Omni3-local resolver only rewrites paths under
  `src/nemotron/recipes/omni3/stage1_rl/config/data_prep`; arbitrary relative
  user paths such as `custom/blend.json` remain caller-relative.
