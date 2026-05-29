# task183_runspec_docs_url_revision_pin_embed_omni_s1 knowledge

<!-- METADATA:SESSION=3 -->

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

## Session 3 Closeout Notes

- PR #290 merged to `main` at
  `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa`; PR head was
  `a5cc62bda8bc2aafaf83fadc85937f21a2ebddd4`.
- PM merged-main probe label:
  `PM_MERGED_RUNSPEC_EMBED_OMNI_DOCS_URL_PROBE_PASS`.
- No new product or live-operation knowledge was added during closeout.
