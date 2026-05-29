# task145_super3_core_blend_path_cwd_independence_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- Core repo-local source blends are represented as repo-relative
  `src/nemotron/recipes/...` paths so saved run configs still carry enough
  context to resolve from arbitrary execution CWDs.
- The resolver intentionally only rewrites repo-source paths under
  `src/nemotron/recipes/...`; absolute paths and unrelated relative override
  paths remain unchanged.
- M1-generated Stage1 SFT `agentic_v0` and `qwen_agentic_v0` blend paths remain
  out of scope for this task.
