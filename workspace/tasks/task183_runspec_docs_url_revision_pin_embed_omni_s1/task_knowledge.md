# task183_runspec_docs_url_revision_pin_embed_omni_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- The task-owned docs URL pin is:
  `https://raw.githubusercontent.com/NVIDIA-NeMo/Nemotron/510b6eec33edece3d212a3187b16db3d1b4a8a15/docs/runspec/v1/spec.md`.
- Scope is limited to Embed and Omni3 recipe entrypoints with PEP 723
  `tool.runspec.docs` metadata. Nano3, Super3, and `docs/runspec/v1/spec.md`
  are out of scope for this task.
- Static checks must not execute recipe scripts or submit jobs.

## Session 2 Notes

- After PR #288, branch base is refreshed to
  `df45842edade40c19fd0496f3844ef20653a94cc`; the docs URL pin remains the
  PM-specified assignment commit `510b6eec33edece3d212a3187b16db3d1b4a8a15`.
