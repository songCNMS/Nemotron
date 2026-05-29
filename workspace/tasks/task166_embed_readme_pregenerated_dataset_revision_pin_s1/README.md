# task166_embed_readme_pregenerated_dataset_revision_pin_s1

<!-- METADATA:STATUS=ReadyForGate,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Pin the Embed README pre-generated NVDocs dataset examples to the same
Hugging Face revision already used by the default Stage0 SDG config.

## Scope

- `docs/nemotron/embed/README.md`
- `src/nemotron/recipes/embed/README.md`
- Focused static README/config guard under `tests/recipes/embed/`
- Task/status docs for `intern_nem_dev_3`

## Acceptance

- Both README `load_dataset` examples for
  `nvidia/Retrieval-Synthetic-NVDocs-v1` pass
  `revision='1c0d1856f3fb595b2dda98d4b61061fa6d782d51'`.
- No unpinned direct `load_dataset('nvidia/Retrieval-Synthetic-NVDocs-v1',
  split='train')` example remains in either README.
- Static test ties the README revision to
  `src/nemotron/recipes/embed/stage0_sdg/config/default.yaml`.

## Boundaries

- Docs/static-test only.
- No live `load_dataset`, HF download, Embed SDG/data prep/finetune/eval,
  endpoint calls, W&B, cluster jobs, deploy, artifact ops, direct
  `main`/`master` push, or self-merge.

## PR

- https://github.com/songCNMS/Nemotron/pull/272
