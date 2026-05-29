# task156_embed_sdg_hf_corpus_revision_guard_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Harden Embed Stage0 SDG `hf://` corpus URI handling so Hugging Face corpus
downloads require a concrete pinned revision before `snapshot_download` is
called.

## Scope

- `src/nemotron/recipes/embed/stage0_sdg/data_prep.py`
- `tests/recipes/embed/test_hf_corpus_download.py`
- Task/status docs for `intern_nem_dev_3`

## Acceptance

- Local path corpus behavior is unchanged.
- Pinned default `hf://` corpus URI keeps resolving and passes the pinned
  revision to `snapshot_download`.
- Missing revisions, floating refs, branch/tag names, `refs/*` style refs, and
  non-SHA revisions are rejected before `snapshot_download` is called.

## Boundaries

- No live HF download, corpus generation, data prep, train/eval, endpoint,
  W&B, cluster, deploy, artifact download, direct `main`/`master` push, or
  self-merge.
